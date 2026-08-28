from Npp import editor, console
import re

# --- CONFIGURATION ---
TAB_WIDTH = 4
ALIGN_KEYWORDS = ['AS', 'THEN', 'ELSE', 'IN', 'LET', '=', 'FROM', 'WHERE', 'AND', 'OR']

console.show()
console.clear()

class Token:
    def __init__(self, kind, value, depth, line_num):
        self.kind = kind
        self.value = value
        self.depth = depth
        self.line_num = line_num

class RobustFormatter:
    def __init__(self, text):
        self.text = text
        self.len = len(text)
        self.tokens = []
        self.pos = 0
        self.depth = 0
        self.line = 1
        self.name_map = {} # Remembers variable renames

    def peek(self, length=1):
        if self.pos + length > self.len: return ""
        return self.text[self.pos : self.pos + length]

    def consume(self, length=1):
        chunk = self.text[self.pos : self.pos + length]
        self.pos += length
        return chunk

    def tokenize(self):
        console.write("Tokenizing %d characters...\n" % self.len)
        
        while self.pos < self.len:
            char = self.text[self.pos]
            
            # 1. STRINGS (Handle escaped quotes safely)
            if char in ('"', "'"):
                quote_char = char
                val = self.consume() 
                while self.pos < self.len:
                    curr = self.consume()
                    val += curr
                    if curr == quote_char:
                        if len(val) > 1 and val[-2] != '\\': # Check for escape
                            break
                self.tokens.append(Token('STRING', val, self.depth, self.line))
                continue

            # 2. COMMENTS (Single Line)
            if char in ('-', '/') and (self.peek(2) == '--' or self.peek(2) == '//'):
                val = self.consume(2)
                while self.pos < self.len:
                    curr = self.consume()
                    val += curr
                    if curr == '\n': 
                        self.line += 1
                        break
                self.tokens.append(Token('COMMENT', val.strip(), self.depth, self.line))
                continue

            # 3. COMMENTS (Block /* ... */)
            if char == '/' and self.peek(2) == '/*':
                val = self.consume(2)
                while self.pos < self.len:
                    curr = self.consume()
                    val += curr
                    if val.endswith('*/'): break
                    if curr == '\n': self.line += 1
                self.tokens.append(Token('COMMENT', val, self.depth, self.line))
                continue

            # 4. BRACKETS (Depth Control)
            if char in '([{' :
                self.tokens.append(Token('BRACKET_O', char, self.depth, self.line))
                self.depth += 1
                self.pos += 1
                continue

            if char in ')]}':
                self.depth = max(0, self.depth - 1)
                self.tokens.append(Token('BRACKET_C', char, self.depth, self.line))
                self.pos += 1
                continue

            # 5. COMMAS
            if char == ',':
                self.tokens.append(Token('COMMA', char, self.depth, self.line))
                self.pos += 1
                continue

            # 6. WORDS (Variables & Keywords)
            if char.isalpha() or char == '_':
                val = char
                self.pos += 1
                while self.pos < self.len:
                    c = self.peek()
                    if c.isalnum() or c == '_':
                        val += self.consume()
                    else:
                        break
                
                # RECURRING VARIABLE RENAMING
                if len(val) > 3 and not val.isupper() and val.upper() not in ALIGN_KEYWORDS:
                    # Ignore existing prefixes
                    if not any(val.startswith(p) for p in ['tbl', 'lst', 'rec']):
                        if val not in self.name_map:
                            # Create new name: varName
                            self.name_map[val] = 'var' + val[0].upper() + val[1:]
                        val = self.name_map[val]

                self.tokens.append(Token('WORD', val, self.depth, self.line))
                continue

            # 7. NEWLINES
            if char == '\n':
                self.line += 1
                self.tokens.append(Token('NL', char, self.depth, self.line))
                self.pos += 1
                continue

            # 8. WHITESPACE (Skip it, we rebuild it)
            if char.isspace():
                self.pos += 1
                continue

            # 9. MISC (Operators like +, -, *)
            self.tokens.append(Token('MISC', char, self.depth, self.line))
            self.pos += 1

    def format(self):
        output = []
        
        # Calculate Vertical Alignment Widths
        max_align_width = 0
        for i in range(1, len(self.tokens)):
            if self.tokens[i].value.upper() in ALIGN_KEYWORDS:
                prev = self.tokens[i-1]
                if prev.kind in ['WORD', 'MISC']:
                    max_align_width = max(max_align_width, len(prev.value))
        
        for i, t in enumerate(self.tokens):
            indent = "\t" * t.depth
            
            if t.kind == 'NL': continue # Skip old newlines
            
            # Context-Aware Formatting
            prev = self.tokens[i-1] if i > 0 else None
            
            if t.kind == 'COMMA':
                # Rule: Leading Comma on new line
                output.append("\n" + indent + ",\t")
                
            elif t.kind == 'BRACKET_O':
                # Rule: Open bracket gets new line + indent
                output.append(t.value + "\n" + indent + "\t")
                
            elif t.kind == 'BRACKET_C':
                output.append("\n" + indent + t.value)
                
            elif t.value.upper() in ALIGN_KEYWORDS:
                # Vertical Alignment Logic
                padding = ""
                if prev and prev.kind in ['WORD', 'MISC']:
                    needed = max(0, max_align_width - len(prev.value))
                    tabs = (needed // TAB_WIDTH) + 1
                    padding = "\t" * tabs
                output.append(padding + t.value + " ")
                
            elif t.kind == 'COMMENT':
                output.append("\n" + indent + t.value + "\n" + indent)
                
            else:
                space = ""
                if prev and prev.kind in ['WORD', 'MISC'] and t.kind in ['WORD', 'MISC']:
                    space = " "
                output.append(space + t.value)
                
        return "".join(output)

# --- EXECUTION WITH NULL-BYTE PROTECTION ---
try:
    start_sel = editor.getSelectionStart()
    end_sel = editor.getSelectionEnd()
    
    if start_sel == end_sel:
        console.write("Error: No text selected.\n")
    else:
        # Step 1: Attempt to read text
        raw_code = editor.getTextRange(start_sel, end_sel)
        
        # Step 2: Safety Check for Null Bytes
        expected_len = end_sel - start_sel
        if len(raw_code) < expected_len:
            console.write("WARNING: Selection truncated! (Found %d chars, expected %d)\n" % (len(raw_code), expected_len))
            console.write("Likely cause: Invisible Null Byte (\\x00). Attempting binary fix...\n")
            
            # Manually read char-by-char to skip nulls (Slow but safe)
            clean_code = []
            for i in range(start_sel, end_sel):
                c = editor.getCharAt(i)
                if c != 0: # Skip null bytes
                    clean_code.append(chr(c))
            raw_code = "".join(clean_code)
            console.write("Binary fix complete. New length: %d\n" % len(raw_code))

        # Step 3: Run Parser
        formatter = RobustFormatter(raw_code)
        formatter.tokenize()
        new_code = formatter.format()
        
        # Step 4: Replace
        editor.beginUndoAction()
        editor.setTargetStart(start_sel)
        editor.setTargetEnd(end_sel)
        editor.replaceTarget(new_code)
        editor.endUndoAction()
        
        console.write("Success! Formatted %d tokens.\n" % len(formatter.tokens))

except Exception as e:
    if editor.getInUndoAction(): editor.endUndoAction()
    console.write("CRITICAL ERROR: " + str(e) + "\n")