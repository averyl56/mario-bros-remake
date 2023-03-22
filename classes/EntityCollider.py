'''Checks if entity has collided with another entity'''

class EntityCollider:
    def __init__(self, entity):
        self.entity = entity

    def check(self, target):
        if self.entity.rect.colliderect(target.rect):
            return self.determineSide(target.rect, self.entity.rect) #entities have collided
        return CollisionState(False, False)

    def determineSide(self, rect1, rect2):
        if (
            rect1.collidepoint(rect2.bottomleft)
            or rect1.collidepoint(rect2.bottomright)
            or rect1.collidepoint(rect2.midbottom) #entity 2 fell ontop of or hit bottom of entity 1
        ):
            if rect2.collidepoint((rect1.midleft[0] / 2, rect1.midleft[1] / 2)) or rect2.collidepoint((rect1.midright[0] / 2, rect1.midright[1] / 2)):
                return CollisionState(True, False) #entities hit eachothers side or bottom
            else:
                if self.entity.vel.y > 0 and rect2.y <= rect1.y:
                    return CollisionState(True, True) #entity fell ontop of other
        return CollisionState(True, False)

class CollisionState:
    def __init__(self, _isColliding, _isTop):
        self.isColliding = _isColliding
        self.isTop = _isTop
