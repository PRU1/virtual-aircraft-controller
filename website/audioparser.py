import bosontranscriptor as bt

keywords = {
    "climb": "alt",
    "descend": "alt",
    "increase": "speed",
    "reduce": "speed",
    "decrease": "speed",
    "turn": "heading",
    "land": "clearL",
    "take": "clearTO",
    "takeoff": "clearTO"
}

numbers = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "thousand": 1000}

file = "../airlines.txt"
airlines1 = {}
airlinesm = {}

x = open(file)
raw = x.read()
rawlist = raw.split("\n")
for entry in rawlist:
    if not entry.strip():  # Skip empty lines
        continue
    airline_info = entry.split()
    if len(airline_info) < 3:  # Skip incomplete entries
        continue
    if len(airline_info) == 3:
        airlines1[airline_info[1].lower()] = airline_info[0]
    else:
        # Create a tuple of lowercase words for multi-word airline names
        words_tuple = tuple(word.lower() for word in airline_info[1:-1])
        airlinesm[words_tuple] = airline_info[0]

def extract_instructions(transcript):
    recipient_specified = False
    recipient = None
    instructions = []
    i = 0
    
    while i < len(transcript):  # Fixed: was i <= len(transcript) which causes index error
        if not recipient_specified:
            # Check for single-word airline
            if transcript[i] in airlines1:
                recipient = airlines1[transcript[i]]
                i += 1
                # Check if we have enough words for flight number
                if i + 2 < len(transcript):
                    try:
                        flight_digits = []
                        for j in range(3):  # Get 3 digits for flight number
                            if i + j < len(transcript) and transcript[i + j] in numbers:
                                flight_digits.append(str(numbers[transcript[i + j]]))
                            else:
                                break
                        if len(flight_digits) == 3:
                            recipient += "".join(flight_digits)
                            i += 3
                            recipient_specified = True
                    except (KeyError, IndexError):
                        pass
            
            # Check for multi-word airlines (2 words)
            elif i + 1 < len(transcript):
                two_word = tuple(transcript[i:i+2])
                if two_word in airlinesm:
                    recipient = airlinesm[two_word]
                    i += 2
                    # Get flight number
                    if i + 2 < len(transcript):
                        try:
                            flight_digits = []
                            for j in range(3):
                                if i + j < len(transcript) and transcript[i + j] in numbers:
                                    flight_digits.append(str(numbers[transcript[i + j]]))
                                else:
                                    break
                            if len(flight_digits) == 3:
                                recipient += "".join(flight_digits)
                                i += 3
                                recipient_specified = True
                        except (KeyError, IndexError):
                            pass
                
                # Check for multi-word airlines (3 words)
                elif i + 2 < len(transcript):
                    three_word = tuple(transcript[i:i+3])
                    if three_word in airlinesm:
                        recipient = airlinesm[three_word]
                        i += 3
                        # Get flight number
                        if i + 2 < len(transcript):
                            try:
                                flight_digits = []
                                for j in range(3):
                                    if i + j < len(transcript) and transcript[i + j] in numbers:
                                        flight_digits.append(str(numbers[transcript[i + j]]))
                                    else:
                                        break
                                if len(flight_digits) == 3:
                                    recipient += "".join(flight_digits)
                                    i += 3
                                    recipient_specified = True
                            except (KeyError, IndexError):
                                pass
            
            if not recipient_specified:
                i += 1

        else:
            # Look for command keywords
            if transcript[i] in keywords:
                command = keywords[transcript[i]]
                if command == "clearL" or command == "clearTO":
                    instructions.extend([command, 1])
                    i += 1
                else:
                    i += 1
                    # Find the next number
                    while i < len(transcript) and transcript[i] not in numbers:
                        i += 1
                    
                    if i < len(transcript):
                        value = 0
                        while i < len(transcript) and transcript[i] in numbers:
                            if transcript[i] == "thousand":
                                value = value * 1000
                            else:
                                value = value * 10 + numbers[transcript[i]]
                            i += 1
                        instructions.extend([command, value])
            else:
                i += 1
    
    if recipient and instructions:
        return [recipient] + instructions  # Fixed: was using .extend() which returns None
    else:
        return None

def parse_audio(audio_path):
    transcript = bt.transcribe_audio(audio_path)
    transcript_words = transcript.lower().split()
    instructions = extract_instructions(transcript_words)
    return instructions