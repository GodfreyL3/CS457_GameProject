
## Preface
I made a base diagram from scratch and then used the mermaid AI to help me clarify some things and fill in some gaps.

## Prompts
- This is my initial server state diagram for a text-based rpg/rougulike for two players over a command prompt. pretty simple, but is there anything that doesnt make sense or that I could clarify better?
- I wanted to keep the "Levels" Pretty general as I also wanted to include shops and events as "Levels". Structurally they would be the same, that way I can copy code. Also turn order will be handled by a DEX stat
- Can you update the diagram to use area-based names instead of level-based names? (Suggested by Mermaid)
- Could you also flesh out the player connect and creation bit the way you suggested before?
- any more thoughts?
- So my plan for fight rewards, I actuially plan to have enemies on death drop items that "cost" 0 coin on death. They can buy these items on a turn in the middle of a fight (if they want to use it that way). The progression turn will only be available if the stage has 0 enemies. Actually: is there anything you could add to the diagram to reflect this without getting to precise?
- Actually, I think I'm gonna keep the last one for the sake of simplicity. Is there any states/arrows you would add for invalid moves or unexpected disconnections?