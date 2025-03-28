import umidiparser
import gmfunctions

# Configuration
file_name = "SMASH MOUTH.All star.mid"
midi_to_key = {
    48: "z", 49: "s", 50: "x", 51: "d", 52: "c", 53: "v", 54: "g",
    55: "b", 56: "h", 57: "n", 58: "j", 59: "m", 60: "q", 61: "2",
    62: "w", 63: "3", 64: "e", 65: "r", 66: "5", 67: "t", 68: "6",
    69: "y", 70: "7", 71: "u"
}


def transpose_note(note, midi_to_key):
    """Transpose note to nearest playable note, preserving pitch class"""
    playable_notes = sorted(midi_to_key.keys())
    if note in playable_notes:
        return note

    # Get pitch class (C, C#, D, etc.)
    pitch_class = note % 12
    # Find all matching pitch classes in playable range
    candidates = [n for n in playable_notes if n % 12 == pitch_class]

    if candidates:
        # Find closest octave match
        closest = min(candidates, key=lambda x: abs(x - note))
        return closest
    else:
        # Fallback to nearest note if exact pitch class unavailable
        closest = min(playable_notes, key=lambda x: abs(x - note))
        return closest


# Parse MIDI and group by channel
mf = umidiparser.MidiFile(file_name)
channels = {}  # {channel_num: [notes]}
current_time_us = 0  # Track cumulative time in microseconds

program_changes = {}

for event in mf:
    current_time_us += event.delta_us

    if event.status == umidiparser.NOTE_ON and event.velocity > 0:
        event_type = 'note_on'
    elif event.status == umidiparser.NOTE_OFF or (event.status == umidiparser.NOTE_ON and event.velocity == 0):
        event_type = 'note_off'
    elif event.status == umidiparser.PROGRAM_CHANGE:
        program_changes[event.channel] = event.program
        continue
    else:
        continue

    # Transpose note if needed
    original_note = event.note
    processed_note = (original_note if original_note in midi_to_key
                      else transpose_note(original_note, midi_to_key))

    channel = event.channel
    if channel not in channels:
        channels[channel] = []

    channels[channel].append({
        'type': event_type,
        'original_note': original_note,  # Keep for debugging
        'note': processed_note,
        'time_us': current_time_us,
        'channel': channel
    })

channel_info = {}

for channel in range(16):  # MIDI has 16 channels (0-15)
    if channel == 9:  # Channel 10 (percussion)
        channel_info[channel] = "Percussion (Drums)"
    elif channel in program_changes:
        program_num = program_changes[channel]
        instrument = gmfunctions.program_name(program_num)  # Use GM helper
        channel_info[channel] = f"Melodic ({instrument})"
    else:
        channel_info[channel] = "Melodic (No Program Change)"

print("\nAvailable Channels (Channel: Event Count - Role):")
for channel in sorted(channels.keys()):
    notes = channels[channel]
    role = channel_info.get(channel, "Unknown")
    print(f"  {channel}: {len(notes)} events - {role}")

    # Show drum note names for Channel 10
    if channel == 9:
        drum_notes = set(n['original_note'] for n in notes)
        print("    * Drum notes detected:")
        for note in sorted(drum_notes):
            try:
                print(f"      {note}: {gmfunctions.percussion_name(note)}")  # Use GM helper
            except KeyError:
                print(f"      {note}: Unknown drum")

# User selects channels
selected = input("\nEnter channels to include (comma-separated): ").strip()
selected_channels = [int(c) for c in selected.split(",") if c.strip().isdigit()]

# Merge selected channels and sort by time
selected_notes = []
for channel in selected_channels:
    if channel in channels:
        selected_notes.extend(channels[channel])
selected_notes.sort(key=lambda x: x['time_us'])

# Calculate delays (convert μs → ms)
notes_ms = []
prev_time_ms = 0

for note in selected_notes:
    current_time_ms = note['time_us'] / 1000
    delay_ms = current_time_ms - prev_time_ms

    notes_ms.append({
        'type': note['type'],
        'note': note['note'],
        'delay_ms': delay_ms,
        'channel': note['channel'],
        'original_note': note.get('original_note', note['note'])  # For debugging
    })
    prev_time_ms = current_time_ms


# Generate AHK script with proper down/up commands
def generate_ahk_script(notes_ms, midi_to_key):
    ahk_script = """#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode "Input"
SetWorkingDir A_ScriptDir

~::PlaySong()
Esc::ExitApp()

PlaySong() {
"""

    for i, note in enumerate(notes_ms):
        if note['note'] not in midi_to_key:
            continue

        key = midi_to_key[note['note']]
        action = "down" if note['type'] == 'note_on' else 'up'

        if i > 0 and note['delay_ms'] > 0:
            ahk_script += f'    Sleep {int(round(note["delay_ms"]))}\n'

        ahk_script += f'    Send("{{{key} {action}}}")\n'

    ahk_script += "}\n"
    return ahk_script


# Save to file
output_file = file_name.replace(".mid", ".ahk")
with open(output_file, "w") as f:
    f.write(generate_ahk_script(notes_ms, midi_to_key))

print(f"\nSuccess! Generated AHK script: {output_file}")