
import pygame
from pathlib import Path
from animation import SpriteAnimation
from projectiles import FlyingKnife
from collisions import collision_rect

class Character(pygame.sprite.Sprite):
    def __init__(self, image_path, position, speed, width=800):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=position)
        self.speed =  speed #speed
        self.win_width = width
        self.keys_pressed = {"left": False, "right": False}
        self.is_action = False
        self.name = ""
        self.animation = None
        self.facing = 1
        self.is_moving = False
        self.solids=[]

    def body_rect(self):
        return self.rect.inflate(-min(20,self.rect.width//3),-4)

    def solid_rects(self):
        objects=list(self.solids)+list(getattr(self,'platforms',()))
        return [collision_rect(c) for c in objects if c is not self and getattr(c,'holder',None) is not self]

    def move(self):
        previous_x = self.rect.x
        before=self.body_rect()
        direction = int(self.keys_pressed['right']) - int(self.keys_pressed['left'])
        self.rect.x += direction * self.speed
        self.rect.x = max(0, min(self.rect.x, self.win_width - self.rect.width))
        after=self.body_rect()
        for obstacle in self.solid_rects():
            if before.top < obstacle.bottom and before.bottom > obstacle.top:
                if direction>0 and before.right<=obstacle.left and after.right>obstacle.left:
                    self.rect.x-=after.right-obstacle.left
                elif direction<0 and before.left>=obstacle.right and after.left<obstacle.right:
                    self.rect.x+=obstacle.right-after.left
                after=self.body_rect()
        self.is_moving = self.rect.x != previous_x
        if self.is_moving:
            self.facing = 1 if self.rect.x > previous_x else -1

    def update(self, dt=1/60):
        if self.animation:
            self.image = self.animation.frame(self.animation_state(), dt, self.facing)

    def animation_state(self):
        return 'walk' if self.is_moving else 'idle'


    def action(self):
        pass



class Acrobat(Character):
    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.jump_speed = 10
        self.gravity = 1
        self.vertical_velocity = 0
        self.landing_remaining = 0.0
        self.name = "Acrobat"
        self.floor_y=None
        self.platforms=[]
        self.animation = SpriteAnimation(
            Path(__file__).resolve().parent.parent / 'img' / 'acrobat_animations.png',
            (48, 64), {'idle': (0, (0, 1, 2, 3, 2, 1), 4), 'walk': (1, (0, 1, 2, 3), 8),
                       'rise': (2, (0,), 1), 'apex': (2, (1,), 1),
                       'fall': (2, (2,), 1), 'land': (2, (3,), 1)})
        self.image = self.animation.frame('idle', 0)
        # Keep the original foot position when changing to a padded frame.
        feet = self.rect.midbottom
        self.rect = self.image.get_rect(midbottom=(feet[0], feet[1]+2))

    def jump(self):
        # Toteuta hyppytoiminto
        if not self.is_action:
            print("Jumping!")
            self.is_action = True
            self.jump_start_y = self.rect.y
            self.vertical_velocity = -self.jump_speed
            self.landing_remaining = 0.0

    def animation_state(self):
        if self.is_action:
            if abs(self.vertical_velocity) <= 2:
                return 'apex'
            return 'rise' if self.vertical_velocity < 0 else 'fall'
        if self.landing_remaining > 0:
            return 'land'
        return super().animation_state()



    def action(self):
        self.jump()

    def update(self, dt=1/60):
        self.landing_remaining = max(0.0, self.landing_remaining - max(0.0, dt))
        if self.floor_y is not None:
            self.update_platforms()
            super().update(dt)
            return
        if self.is_action:
            self.rect.y += self.vertical_velocity
            self.vertical_velocity += self.gravity
            if self.vertical_velocity >= 0 and self.rect.y >= self.jump_start_y:
                self.rect.y = self.jump_start_y
                self.is_action = False
                self.vertical_velocity = 0
                self.landing_remaining = 0.08
        super().update(dt)

    def update_platforms(self):
        before=self.body_rect()
        obstacles=self.solid_rects()
        surfaces_rects=obstacles
        supported=any(before.bottom==r.top and before.left<r.right and before.right>r.left for r in surfaces_rects)
        if not self.is_action and self.rect.y<self.floor_y and not supported:
            self.is_action=True
            self.vertical_velocity=0
        if not self.is_action: return
        velocity=self.vertical_velocity
        self.rect.y+=velocity
        self.vertical_velocity+=self.gravity
        after=self.body_rect()
        landed=False
        if velocity>=0:
            surfaces=[r.top for r in surfaces_rects if before.bottom<=r.top<=after.bottom
                      and after.left<r.right and after.right>r.left]
            if surfaces:
                self.rect.y-=after.bottom-min(surfaces)
                landed=True
            elif self.rect.y>=self.floor_y:
                self.rect.y=self.floor_y
                landed=True
        else:
            ceilings=[r.bottom for r in obstacles if after.top<=r.bottom<=before.top
                      and after.left<r.right and after.right>r.left]
            if ceilings:
                self.rect.y+=max(ceilings)-after.top
                self.vertical_velocity=0
        if landed:
            self.is_action=False
            self.vertical_velocity=0
            self.landing_remaining=.08

class KnifeThrower(Character):
    THROW_FRAME_SECONDS = 0.12
    THROW_DURATION = 4 * THROW_FRAME_SECONDS

    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.name = "Knife thrower"
        self.throw_elapsed = 0.0
        self.projectiles = pygame.sprite.Group()
        self.knife_released = False
        self.animation = SpriteAnimation(
            Path(__file__).resolve().parent.parent/'img'/'knife_animations.png',
            (72,80), {'idle': (0,(1,),1), 'walk': (0,(0,1,2,3),8),
                      **{'throw_'+str(i): (1,(i,),1) for i in range(4)}})
        self.image = self.animation.frame('idle',0)
        # Keep the spawn x and visible feet height; the larger cell has arm padding.
        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.bottom+2-80))

    def throw_knife(self):
        if not self.is_action:
            self.is_action = True
            self.throw_elapsed = 0.0
            self.knife_released = False
            self.is_moving = False
            self.image = self.animation.frame('throw_0',0,self.facing)

    def move(self):
        if self.is_action:
            self.is_moving = False
        else:
            super().move()

    def animation_state(self):
        if self.is_action:
            return 'throw_'+str(min(3,int(self.throw_elapsed/self.THROW_FRAME_SECONDS)))
        return super().animation_state()

    def update(self, dt=1/60):
        self.projectiles.update(dt)
        if self.is_action:
            previous_elapsed = self.throw_elapsed
            self.throw_elapsed += max(0.0,dt)
            release_time = 2*self.THROW_FRAME_SECONDS
            if not self.knife_released and self.throw_elapsed >= release_time:
                self.knife_released = True
                hand_x = self.rect.left + (69 if self.facing > 0 else 3)
                knife = FlyingKnife((hand_x,self.rect.top+19),self.facing,(self.win_width,600),self.solids)
                self.projectiles.add(knife)
                # Integrate only the part of this update after the release instant.
                knife.update(max(0.0,self.throw_elapsed-max(previous_elapsed,release_time)))
            if self.throw_elapsed >= self.THROW_DURATION:
                self.is_action = False
        super().update(dt)

    def action(self):
        self.throw_knife()


class Strongman(Character):
    ACTION_SECONDS=0.8

    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.name = "Strong man"
        self.crates=[]
        self.blockers=[]
        self.carried=None
        self.motion=None
        self.motion_elapsed=0.0
        self.is_pushing=False
        self.hint=''
        self.animation=SpriteAnimation(
            Path(__file__).resolve().parent.parent/'img'/'strongman_animations.png',
            (96,80),{'idle':(0,(1,),1),'walk':(0,(0,1,2,3),6),
                     'hold':(1,(3,),1),'carry':(2,(0,1,2,3),5),'push':(3,(0,1,2,3),6),
                     **{'lift_'+str(i):(1,(i,),1) for i in range(4)},
                     **{'lower_'+str(i):(1,(3-i,),1) for i in range(4)}})
        self.image=self.animation.frame('idle',0)
        self.rect=self.image.get_rect(topleft=(self.rect.x,self.rect.bottom+2-80))

    def ground_target(self):
        center=self.rect.left+(84 if self.facing>0 else 12)
        return pygame.Rect(center-20,self.rect.bottom-42,40,40)

    def body_rect(self):
        return pygame.Rect(self.rect.left+32,self.rect.top+2,32,self.rect.height-4)

    def nearby_crate(self):
        # A crate at the extended hands is always reachable for lifting too.
        # Use contact geometry, not is_pushing, so releasing the arrow still works.
        contact=self.push_crate(self.facing)
        if contact is not None:
            return contact
        target=self.ground_target()
        available=[c for c in self.crates if c.holder is None and
                   abs(c.rect.centerx-target.centerx)<=28 and abs(c.rect.bottom-target.bottom)<=4]
        return min(available,key=lambda c:abs(c.rect.centerx-target.centerx),default=None)

    def can_place(self,target):
        return (target.left>=0 and target.right<=self.win_width and
                not any(target.colliderect(c.rect) for c in self.crates if c is not self.carried) and
                not any(target.colliderect(collision_rect(c)) for c in self.blockers if c is not self))

    def move(self):
        self.is_pushing=False
        if self.is_action:
            self.is_moving=False
            return
        direction=int(self.keys_pressed['right'])-int(self.keys_pressed['left'])
        old_facing=self.facing
        if direction:
            self.facing=direction
        crate=self.push_crate(direction) if not self.carried and direction else None
        original_speed=self.speed
        if self.carried or crate:
            self.speed=max(1,self.speed//2)
        before=self.rect.x
        proposed=self.rect.move(direction*self.speed,0)
        if crate and not self.can_place_push(crate,crate.rect.move(direction*self.speed,0)):
            self.is_moving=False
        elif self.carried and (not (0<=proposed.left and proposed.right<=self.win_width) or
                              not self.can_place(self.carried.rect.union(self.carried_target(proposed, moving=bool(direction))))):
            self.is_moving=False
            self.facing=old_facing
            self.hint='Ei tilaa kantaa — siirry vapaaseen suuntaan'
        else:
            saved_solids=self.solids
            if crate:
                self.solids=[obstacle for obstacle in self.solids if obstacle is not crate]
            super().move()
            self.solids=saved_solids
            if crate and self.is_moving:
                crate.rect.x+=self.rect.x-before
                self.is_pushing=True
        self.speed=original_speed

    def push_crate(self,direction):
        hand=self.rect.left+(70 if direction>0 else 26)
        for crate in self.crates:
            gap=(crate.rect.left-hand) if direction>0 else (hand-crate.rect.right)
            if crate.holder is None and -6<=gap<=self.speed+3 and abs(crate.rect.bottom-(self.rect.bottom-2))<=4:
                return crate
        return None

    def can_place_push(self,crate,target):
        return (0<=target.left and target.right<=self.win_width and
                not any(target.colliderect(c.rect) for c in self.crates if c is not crate) and
                not any(target.colliderect(collision_rect(c)) for c in self.blockers if c is not self))

    def animation_state(self):
        if self.motion:
            return self.motion+'_'+str(min(3,int(self.motion_elapsed/(self.ACTION_SECONDS/4))))
        if self.carried:
            return 'carry' if self.is_moving else 'hold'
        if self.is_pushing and self.is_moving:
            return 'push'
        return super().animation_state()

    def carried_target(self,position=None,moving=None):
        position=self.rect if position is None else position
        moving=self.is_moving if moving is None else moving
        phase=3
        if self.motion:
            phase=min(3,int(self.motion_elapsed/(self.ACTION_SECONDS/4)))
            if self.motion=='lower': phase=3-phase
        centers=(84,74,74,74)
        bottoms=(78,65,45,29)
        center=centers[phase]
        bottom=bottoms[phase]
        if not self.motion and moving: bottom=35
        if self.facing<0: center=96-center
        result=pygame.Rect(0,0,40,40)
        result.midbottom=(position.left+center,position.top+bottom)
        return result

    def position_carried(self):
        if self.carried:
            target=self.carried_target()
            if self.can_place(self.carried.rect.union(target)):
                self.carried.rect=target

    def update(self,dt=1/60):
        if self.motion:
            previous_elapsed=self.motion_elapsed
            self.motion_elapsed+=max(0.0,dt)
            if not self.can_place(self.carried.rect.union(self.carried_target())):
                self.motion_elapsed=previous_elapsed
                self.hint='Noston tai laskun tiellä on este'
                super().update(dt)
                return
            if self.motion_elapsed>=self.ACTION_SECONDS:
                if self.motion=='lower':
                    target=self.ground_target()
                    if self.can_place(target):
                        self.carried.rect=target
                        self.carried.holder=None
                        self.carried=None
                    else:
                        self.hint='Ei tilaa laskea — siirry vapaaseen paikkaan'
                self.motion=None
                self.is_action=False
        self.position_carried()
        super().update(dt)


    def lift(self):
        self.action()

    def action(self):
        if self.is_action: return
        self.hint=''
        previous_carried=self.carried
        if self.carried:
            if not self.can_place(self.ground_target()):
                self.hint='Ei tilaa laskea — siirry vapaaseen paikkaan'
                return
            self.motion='lower'
        else:
            crate=self.nearby_crate()
            if crate is None:
                self.hint='Siirry laatikon viereen ja paina välilyöntiä'
                return
            self.carried=crate
            crate.holder=self
            self.motion='lift'
        # Validate the complete path before reserving a prop or starting the action.
        path=self.carried.rect.copy()
        for elapsed in (0,.2,.4,self.ACTION_SECONDS):
            self.motion_elapsed=elapsed
            path=path.union(self.carried_target())
        if not self.can_place(path):
            if previous_carried is None:
                self.carried.holder=None
                self.carried=None
            self.motion=None
            self.hint='Noston tai laskun tiellä on este'
            return
        self.motion_elapsed=0.0
        self.is_action=True
        self.is_moving=False
        self.position_carried()
        self.image=self.animation.frame(self.animation_state(),0,self.facing)
