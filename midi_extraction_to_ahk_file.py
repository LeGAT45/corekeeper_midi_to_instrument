import umidiparser

file_name = "megalovania.mid"
mf = umidiparser.MidiFile(file_name)

# Initialize trackers
channels = []
notes = []
current_time_us = 0  # Track cumulative time in microseconds

for event in mf:
    current_time_us += event.delta_us

    if event.status == umidiparser.NOTE_ON and event.velocity > 0:
        notes.append({
            'type': 'note_on',
            'note': event.note,
            'time_us': current_time_us,
            'channel': event.channel
        })
    elif event.status == umidiparser.NOTE_OFF or (event.status == umidiparser.NOTE_ON and event.velocity == 0):
        notes.append({
            'type': 'note_off',
            'note': event.note,
            'time_us': current_time_us,
            'channel': event.channel
        })

# Convert to milliseconds with proper delays
notes_ms = []
prev_time_ms = 0

for note in notes:
    current_time_ms = note['time_us'] / 1000  # Convert μs to ms
    delay_ms = current_time_ms - prev_time_ms

    notes_ms.append({
        'type': note['type'],
        'note': note['note'],
        'time_ms': current_time_ms,
        'delay_ms': delay_ms,
        'channel': note['channel']
    })
    prev_time_ms = current_time_ms

# Print first 10 notes for verification
print("First 10 note events with millisecond timing:")
for i, note in enumerate(notes_ms[:10]):
    print(f"{i + 1:2d}. {note['type']:7} | Note: {note['note']:3d} | "
          f"Delay: {note['delay_ms']:6.1f}ms | "
          f"Abs: {note['time_ms']:7.1f}ms | "
          f"Channel: {note['channel']}")


# Generate AHK script (using your existing midi_to_key mapping)
def generate_ahk_script(notes_ms, midi_to_key):
    ahk_script = """#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode "Input"
SetWorkingDir A_ScriptDir

~::PlaySong()

Hotkey "Esc", (*) => ExitApp()

PlaySong() {
"""

    for i, note in enumerate(notes_ms):
        if note['note'] not in midi_to_key:
            continue

        key = midi_to_key[note['note']]
        action = "down" if note['type'] == 'note_on' else 'up'

        # Only add delay if needed (not first event and delay > 0)
        if i > 0 and note['delay_ms'] > 0:
            ahk_script += f'    Sleep {int(round(note["delay_ms"]))}\n'

        ahk_script += f'    Send("{{{key} {action}}}")\n'

    ahk_script += "}\n"
    return ahk_script


# Your key mapping
midi_to_key = {
    48: "z", 49: "s", 50: "x", 51: "d", 52: "c", 53: "v", 54: "g",
    55: "b", 56: "h", 57: "n", 58: "j", 59: "m", 60: "q", 61: "2",
    62: "w", 63: "3", 64: "e", 65: "r", 66: "5", 67: "t", 68: "6",
    69: "y", 70: "7", 71: "u"
}

# Generate and save AHK script
ahk_code = generate_ahk_script(notes_ms, midi_to_key)
output_file = file_name.replace(".mid", ".ahk")
with open(output_file, "w") as f:
    f.write(ahk_code)

print(f"\nGenerated AHK script: {output_file}")

for event in mf:
    print(event)