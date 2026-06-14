import os
import json
import anthropic


def assess_character(character_data: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))

    profile = character_data.get('profile', {})
    activity_histories = character_data.get('activity_histories', {})
    display_name = character_data.get('display_name', 'Guardian')

    characters = profile.get('characters', {}).get('data', {})
    char_progressions = profile.get('characterProgressions', {}).get('data', {})
    char_activities = profile.get('characterActivities', {}).get('data', {})
    item_instances = profile.get('itemComponents', {}).get('instances', {}).get('data', {})
    char_inventories = profile.get('characterInventories', {}).get('data', {})

    class_map = {0: 'Titan', 1: 'Hunter', 2: 'Warlock'}

    summary_parts = []
    summary_parts.append(f"Player: {display_name}\n")

    for char_id, char in characters.items():
        class_name = class_map.get(char.get('classType', -1), 'Unknown')
        light = char.get('light', 0)
        minutes = char.get('minutesPlayedTotal', 0)
        summary_parts.append(
            f"\nCharacter: {class_name} | Power Level: {light} | "
            f"Total Playtime: {int(minutes)//60}h {int(minutes)%60}m"
        )

        # Progressions / milestones
        progressions = char_progressions.get(char_id, {})
        milestones = progressions.get('milestones', {})
        if milestones:
            milestone_list = []
            for ms_hash, ms_data in list(milestones.items())[:15]:
                milestone_list.append(f"  - Milestone {ms_hash}: {json.dumps(ms_data)[:200]}")
            summary_parts.append("  Active Milestones (sample):\n" + "\n".join(milestone_list))

        # Recent activities
        history = activity_histories.get(char_id, {})
        activities = history.get('activities', [])
        if activities:
            summary_parts.append(f"  Recent Activities ({len(activities)} shown):")
            for act in activities[:10]:
                details = act.get('activityDetails', {})
                values = act.get('values', {})
                completed = values.get('completed', {}).get('basic', {}).get('value', 0)
                kills = values.get('kills', {}).get('basic', {}).get('displayValue', '?')
                summary_parts.append(
                    f"    - Mode {details.get('mode', '?')} | "
                    f"Completed: {bool(completed)} | Kills: {kills} | "
                    f"Director: {details.get('directorActivityHash', '?')}"
                )

        # Character inventory item power levels (sample)
        inventory = char_inventories.get(char_id, {})
        items = inventory.get('items', [])
        if items and item_instances:
            powered_items = []
            for item in items[:20]:
                inst_id = item.get('itemInstanceId')
                if inst_id and inst_id in item_instances:
                    inst = item_instances[inst_id]
                    pwr = inst.get('primaryStat', {}).get('value', 0)
                    if pwr > 0:
                        powered_items.append(f"    - Item hash {item.get('itemHash')}: Power {pwr}")
            if powered_items:
                summary_parts.append("  Equipped/Inventory Item Power Levels (sample):")
                summary_parts.extend(powered_items[:10])

    data_summary = "\n".join(summary_parts)

    prompt = f"""You are an expert Destiny 2 progression advisor. Below is data pulled from the Bungie API for a player's account. Analyze it and provide a thorough, actionable assessment.

=== PLAYER DATA ===
{data_summary}

=== YOUR TASK ===
Based on this data, provide a detailed assessment in Markdown format covering:

1. **Power Level Analysis** - Current power level for each character, how close they are to the soft cap, hard cap, and pinnacle cap. What activities are most efficient for increasing power.

2. **Gear Slot Assessment** - Based on the item power levels shown, identify which gear slots are likely dragging down the average and should be prioritized for upgrades.

3. **Activity Recommendations** - Specific activities to run:
   - If below soft cap (~1900): Focus on world drops, story missions, patrol zones
   - If at soft cap: Run Nightfalls, Crucible, Gambit for powerful rewards
   - If near hard cap (~1960): Focus on pinnacle reward sources (raids, dungeons, weekly challenges)
   - Raids to consider: Last Wish, Garden of Salvation, Deep Stone Crypt, Vault of Glass, King's Fall, Root of Nightmares, Crota's End, Salvation's Edge
   - Dungeons: Prophecy, Grasp of Avarice, Duality, Spire of the Watcher, Ghosts of the Deep, Warlord's Ruin

4. **Milestone Priorities** - Which weekly milestones are worth completing for pinnacle/powerful gear drops.

5. **Prioritized "What To Do Next" List** - A numbered, prioritized action list the player should follow this week to make the most progression gains.

6. **Build Suggestions** - Based on the character class and current progression level, briefly suggest what type of build or subclass to focus on.

Be specific and actionable. Use the actual power numbers from the data. If data is limited, provide general advice based on what's visible."""

    message = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=2048,
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    return message.content[0].text
