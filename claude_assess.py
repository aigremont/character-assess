# claude_assess.py
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
    char_inventories = profile.get('characterInventories', {}).get('data', {})
    item_instances = profile.get('itemComponents', {}).get('instances', {}).get('data', {})
    milestones = profile.get('characterProgressions', {}).get('data', {})

    # Build a summarized data structure to keep prompt size reasonable
    char_summaries = []
    for char_id, char in characters.items():
        class_map = {0: 'Titan', 1: 'Hunter', 2: 'Warlock'}
        race_map = {0: 'Human', 1: 'Awoken', 2: 'Exo'}

        summary = {
            'character_id': char_id,
            'class': class_map.get(char.get('classType', 0), 'Unknown'),
            'race': race_map.get(char.get('raceType', 0), 'Unknown'),
            'light_level': char.get('light', 0),
            'minutes_played': char.get('minutesPlayedTotal', 0),
        }

        # Add milestone data if available
        char_prog = char_progressions.get(char_id, {})
        ms_data = char_prog.get('milestones', {})
        milestone_list = []
        for ms_hash, ms in list(ms_data.items())[:10]:  # limit to 10
            milestone_list.append({
                'hash': ms_hash,
                'completed': ms.get('endDate', None) is not None,
                'activities': [a.get('activityHash') for a in ms.get('activities', [])],
            })
        summary['milestones'] = milestone_list

        # Add recent activities
        acts = activity_histories.get(char_id, {})
        recent = []
        for act in acts.get('activities', [])[:10]:
            values = act.get('values', {})
            recent.append({
                'activityHash': act.get('activityDetails', {}).get('referenceId'),
                'mode': act.get('activityDetails', {}).get('mode'),
                'completed': values.get('completed', {}).get('basic', {}).get('value', 0),
                'deaths': values.get('deaths', {}).get('basic', {}).get('value', 0),
                'kills': values.get('kills', {}).get('basic', {}).get('value', 0),
                'period': act.get('period', ''),
            })
        summary['recent_activities'] = recent

        # Add equipped items (inventory)
        inv = char_inventories.get(char_id, {})
        equipped_items = []
        for item in inv.get('items', [])[:20]:
            item_instance_id = item.get('itemInstanceId')
            instance_data = item_instances.get(item_instance_id, {}) if item_instance_id else {}
            equipped_items.append({
                'itemHash': item.get('itemHash'),
                'bucketHash': item.get('bucketHash'),
                'primaryStat': instance_data.get('primaryStat', {}),
                'itemLevel': instance_data.get('itemLevel', 0),
                'quality': instance_data.get('quality', 0),
            })
        summary['inventory_sample'] = equipped_items

        char_summaries.append(summary)

    data_json = json.dumps(char_summaries, indent=2)

    prompt = f"""You are a Destiny 2 expert advisor. Below is character data for the Guardian "{display_name}".

The data includes:
- Character class, race, and current Power/Light level
- Recent activity history (last 10 activities per character)
- Milestone data (weekly/daily objectives)
- A sample of inventory items with their power levels

Character Data:
```json
{data_json}
```

Please provide a detailed progression assessment in Markdown format covering:

## 1. Current Status
- Summary of each character and their Power level
- Overall Guardian progression stage (early/mid/late game)

## 2. Power Level Analysis
- Current power level assessment
- What activities to focus on to increase Power level efficiently
- Gap between current level and the current soft/power/pinnacle caps (if determinable)

## 3. Gear Slot Recommendations
- Based on inventory data, identify likely weak gear slots
- Suggest priority slots to upgrade first

## 4. Activity Recommendations
- Specific activities to run based on current progression (raids, dungeons, Nightfalls, story missions, etc.)
- Weekly activities worth prioritizing
- Any milestones that appear worth completing

## 5. Prioritized "What To Do Next" List
A numbered list of the top 5-7 actions the Guardian should take, in priority order.

Keep the assessment practical, specific to what the data shows, and actionable. If certain data is missing or unclear, make reasonable assumptions based on power level."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text
