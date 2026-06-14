import json


def build_prompt(character_data: dict) -> str:
    profile = character_data.get('profile', {})
    activity_histories = character_data.get('activity_histories', {})
    display_name = character_data.get('display_name', 'Guardian')

    characters = profile.get('characters', {}).get('data', {})
    char_progressions = profile.get('characterProgressions', {}).get('data', {})
    char_inventories = profile.get('characterInventories', {}).get('data', {})
    item_instances = profile.get('itemComponents', {}).get('instances', {}).get('data', {})

    class_map = {0: 'Titan', 1: 'Hunter', 2: 'Warlock'}
    race_map = {0: 'Human', 1: 'Awoken', 2: 'Exo'}

    lines = [f"Player: {display_name}\n"]

    for char_id, char in characters.items():
        class_name = class_map.get(char.get('classType', -1), 'Unknown')
        race_name = race_map.get(char.get('raceType', -1), 'Unknown')
        light = char.get('light', 0)
        minutes = int(char.get('minutesPlayedTotal', 0))
        lines.append(
            f"Character: {race_name} {class_name} | Power Level: {light} | "
            f"Playtime: {minutes // 60}h {minutes % 60}m"
        )

        # Milestones
        progressions = char_progressions.get(char_id, {})
        milestones = progressions.get('milestones', {})
        if milestones:
            lines.append(f"  Milestones ({len(milestones)} active):")
            for ms_hash, ms in list(milestones.items())[:15]:
                activities = [str(a.get('activityHash', '')) for a in ms.get('activities', [])]
                lines.append(
                    f"    - hash:{ms_hash} activities:[{', '.join(activities[:3])}]"
                )

        # Recent activities
        history = activity_histories.get(char_id, {})
        activities = history.get('activities', [])
        if activities:
            lines.append(f"  Recent Activities:")
            for act in activities[:10]:
                details = act.get('activityDetails', {})
                values = act.get('values', {})
                completed = bool(values.get('completed', {}).get('basic', {}).get('value', 0))
                kills = values.get('kills', {}).get('basic', {}).get('displayValue', '?')
                mode = details.get('mode', '?')
                lines.append(
                    f"    - mode:{mode} completed:{completed} kills:{kills}"
                )

        # Inventory power levels
        inventory = char_inventories.get(char_id, {})
        items = inventory.get('items', [])
        powered = []
        for item in items[:30]:
            inst_id = item.get('itemInstanceId')
            if inst_id and inst_id in item_instances:
                pwr = item_instances[inst_id].get('primaryStat', {}).get('value', 0)
                bucket = item.get('bucketHash', '')
                if pwr > 0:
                    powered.append(f"bucket:{bucket} power:{pwr}")
        if powered:
            lines.append(f"  Gear Power Levels (sample):")
            for p in powered[:12]:
                lines.append(f"    - {p}")

        lines.append("")

    data_summary = "\n".join(lines)

    return f"""You are an expert Destiny 2 progression advisor. Below is data pulled from the Bungie API for a player's account. Analyse it and provide a thorough, actionable assessment.

=== PLAYER DATA ===
{data_summary}
=== YOUR TASK ===
Based on this data, provide a detailed assessment covering:

1. **Power Level Analysis** - Current power for each character, how close to soft cap (~1900), hard cap (~1960), and pinnacle cap (~1990). Most efficient activities for increasing power right now.

2. **Gear Slot Assessment** - Based on the item power levels shown, which slots are likely dragging down the average and should be prioritised for upgrades (use bucket hashes to infer slot types if needed).

3. **Activity Recommendations** - Specific activities to run based on current power:
   - Below soft cap: world drops, story missions, patrol zones
   - At soft cap: Nightfalls, Crucible, Gambit for powerful rewards
   - Near hard cap: pinnacle sources — raids, dungeons, weekly challenges
   - Raids: Last Wish, Garden of Salvation, Deep Stone Crypt, Vault of Glass, King's Fall, Root of Nightmares, Crota's End, Salvation's Edge
   - Dungeons: Prophecy, Grasp of Avarice, Duality, Spire of the Watcher, Ghosts of the Deep, Warlord's Ruin

4. **Milestone Priorities** - Which weekly milestones are worth completing for pinnacle/powerful drops.

5. **Prioritised "What To Do Next" List** - A numbered action list for this week to maximise progression gains.

6. **Build Suggestions** - Based on the character class and progression level, briefly suggest a subclass or build direction to focus on.

Be specific and use the actual numbers from the data. If data is limited, give general advice based on what's visible."""
