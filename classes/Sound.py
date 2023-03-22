from pygame import mixer


class Sound:
    def __init__(self):
        self.music_channel = mixer.Channel(0)
        self.music_channel.set_volume(0.2)
        self.sfx_channel = mixer.Channel(1)
        self.sfx_channel.set_volume(0.3)
        self.top_channel = mixer.Channel(2)
        self.top_channel.set_volume(0.3)

        self.allowSFX = True
        self.allowMusic = True
        self.sounds = {
            "oneup": mixer.Sound("./sfx/1up.wav"),
            "bowser falls": mixer.Sound("./sfx/bowser_falls.wav"),
            "break": mixer.Sound("./sfx/break.wav"),
            "bump": mixer.Sound("./sfx/bump.wav"),
            "castle": mixer.Sound("./sfx/castle.mp3"),
            "coin": mixer.Sound("./sfx/coin.wav"),
            "death": mixer.Sound("./sfx/death.wav"),
            "fireball": mixer.Sound("./sfx/fireball.wav"),
            "firebreath": mixer.Sound("./sfx/firebreath.wav"),
            "fireworks": mixer.Sound("./sfx/fireworks.wav"),
            "flagpole": mixer.Sound("./sfx/flagpole.wav"),
            "gameover": mixer.Sound("./sfx/gameover.wav"),
            "invincible": mixer.Sound("./sfx/invincible.mp3"),
            "big jump": mixer.Sound("./sfx/jump_big.wav"),
            "small jump": mixer.Sound("./sfx/jump_small.wav"),
            "kick": mixer.Sound("./sfx/kick.wav"),
            "overworld": mixer.Sound("./sfx/overworld.mp3"),
            "pause": mixer.Sound("./sfx/pause.wav"),
            "pipe": mixer.Sound("./sfx/pipe.wav"),
            "powerup appears": mixer.Sound("./sfx/powerup_appears.wav"),
            "powerup": mixer.Sound("./sfx/powerup.wav"),
            "princess saved": mixer.Sound("./sfx/princess_saved.mp3"),
            "stage clear": mixer.Sound("./sfx/stage_clear.wav"),
            "stomp": mixer.Sound("./sfx/stomp.wav"),
            "underground": mixer.Sound("./sfx/underground.mp3"),
            "underwater": mixer.Sound("./sfx/underwater.mp3"),
            "vine": mixer.Sound("./sfx/vine.wav"),
            "warning": mixer.Sound("./sfx/warning.wav"),
            "world clear": mixer.Sound("./sfx/world_clear.wav")
        }

    def play_sfx(self, sfx):
        if self.allowSFX:
            self.sfx_channel.play(self.sounds[sfx])

    def play_music(self, music, loop):
        if self.allowMusic:
            self.music_channel.play(self.sounds[music],loops=loop)

    def play_effect(self, sfx):
        if self.allowSFX:
            self.top_channel.play(self.sounds[sfx])
