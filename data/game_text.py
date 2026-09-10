"""All player-facing text for the game lives here. Edit strings below to change in-game text."""

WINDOW_TITLE = "Tibs Journey"

INTERACT_PROMPT = "[E]"
CONTINUE_PROMPT = "[E] Continue"

INTRO_TEXT = [
    "Welcome to Tib's Journey!",
    "Use A/D or the Arrow Keys to move, and W, Up, or Space to jump.",
    "Hold Shift while moving to sprint.",
    "Somewhere out there, four baby dinosaur eggs have been separated from their parents.",
    "Find each lost egg, then bring it back to its worried parent. Press [E] to talk and interact.",
    "Carrying an egg but want a different one? Press [E] while not near anyone to throw it back down.",
    "Good luck, Tib!",
]

DIALOGUE = {
    "yellow_egg": "Oh Tib thank god you are here! You found me! Please return me to my father, please!",
    "yellowdino_ask": "Oh no... I can't find my baby egg anywhere! Please, could you help me look for it?",
    "yellowdino_thanks": "Thank you so much! You really found it! Thank you for collecting my baby egg!",
    "yellowdino_done": "My baby is safe thanks to you, Tib. I can't thank you enough!",

    "blue_egg": "Eep! Please don't leave me here, it's so cold and quiet... Can you carry me home to my mother?",
    "bluedino_ask": "M-my egg rolled away from the nest during the storm... I'm too scared to go looking myself. Could you find it for me?",
    "bluedino_thanks": "You... you actually found her! I was so worried! Thank you, Tib, truly!",
    "bluedino_done": "My little one is finally warm and safe in the nest again. I'll never forget this kindness.",

    "green_egg": "Zzz... huh? Oh! A visitor! Say, would you mind rolling me back over to my dad? I'm much too sleepy to walk.",
    "greendino_ask": "Ohh, I dozed off for just a moment and when I woke up my egg was gone! Old dino brain, ha! Could you help an old timer out?",
    "greendino_thanks": "Well would you look at that! Home safe and sound. Thank you kindly, little one.",
    "greendino_done": "Ahh, nothing like a nap next to my hatchling. Thanks again for finding her, Tib.",

    "red_egg": "Hey! Over here! Get me out of here! and back to my father before he tears this whole jungle apart looking for me!",
    "reddino_ask": "GRRAH! Where is my egg?! I will not rest until my child is found! ...Please, Tib, will you help me search?",
    "reddino_thanks": "You found my egg! I could roar with joy! Thank you, Tib, you have my eternal respect!",
    "reddino_done": "My fierce little one is home. Nothing in this jungle scares me more than losing my child, so... thank you.",
}

DINO_ORDER = ["yellow", "blue", "green", "red"]

DINO_NAMES = {
    "yellow": "the yellow dino family",
    "blue": "the blue dino family",
    "green": "the green dino family",
    "red": "the red dino family",
}

CUTSCENE_ADVANCED_CAPTIONS = {
    "yellow": "The yellow family basks together in the warm sunlight.",
    "blue": "The blue family huddles close, safe from the storm at last.",
    "green": "The green family drifts off into a peaceful, shared nap.",
    "red": "The red family stands proud, roaring together in celebration.",
}

CUTSCENE_ADVANCED_FINALE = "Congratulations, Tib! Every baby dinosaur is home safe."

YOU_WIN_TITLE = "You Win!"
YOU_WIN_SUBTITLE = "Tib the hero!"
