from pygame.sprite import spritecollide, collide_mask


def get_bullet_collisions(ships):
    collisions = []
    for firing_ship in ships:
        bullets = firing_ship.bullets
        for ship in [ship for ship in ships if not (ship.dead or ship is firing_ship)]:

            for colliding in spritecollide(ship.sprite,
                                           [bullet.sprite for bullet in bullets], False, collide_mask):
                for i, bullet in enumerate(bullets):
                    if bullet.sprite == colliding:
                        bullets.pop(i)
                        collisions.append((firing_ship, ship, bullet))
                        continue

    return collisions


def get_ship_collisions(ships):
    collisions = []

    for ship_a in [ship for ship in ships if not ship.dead]:
        for ship_b in [ship for ship in ships if not (ship.dead or ship is ship_a)]:
            if spritecollide(ship_b.sprite, [ship_a.sprite], False, collide_mask):
                collisions.append((ship_a, ship_b))
    return collisions
