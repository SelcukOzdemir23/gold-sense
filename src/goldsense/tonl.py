from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Union, Tuple, Optional

# --- Constants & Regex ---

VERSION = "1.0"
RESERVED_LITERALS = {"true", "false", "null", "undefined", "Infinity", "-Infinity", "NaN"}
NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")

# Extended Header Regex to support optional type hints e.g. key{id:u32,name:str}:
# But for parsing, we largely ignore hints or just capture columns.
# Captures: key, count, cols, rest (value)
HEADER_RE = re.compile(
    r"""^
    (?P<key>[a-zA-Z_]\w*|\[\d+\])    # Key name or [index]
    (?:\[(?P<count>\d+)\])?          # Optional [N]
    (?:\{(?P<cols>[^}]+)\})?         # Optional {col1,col2}
    :\s*                             # Colon and opt whitespace
    (?P<rest>.*)$                    # The rest (value)
    """,
    re.VERBOSE
)

# --- Public API ---

@dataclass(frozen=True)
class TonlEncodeResult:
    text: str
    json_chars: int
    tonl_chars: int
    savings_percent: float

def encode_tonl(data: Any, root_key: str = "root") -> str:
    """
    Generic encoded for any JSON-serializable data to TONL format.
    Adheres to TONL 2.0 style (multiline strings, smart delimiters).
    """
    delimiter = _choose_best_delimiter(data)
    
    lines = [f"#version {VERSION}"]
    if delimiter != ",":
        lines.append(f"#delimiter {delimiter}")

    context = {
        "indent_step": 2, 
        "delimiter": delimiter
    }

    # Root encoding
    if isinstance(data, dict):
        # Flattened root for dicts
        for k, v in data.items():
            encoded = _encode_value(v, k, indent=0, context=context)
            if isinstance(encoded, list):
                lines.extend(encoded)
            else:
                lines.append(encoded)
    else:
        # Wrapper for others
        encoded_root = _encode_value(data, root_key, indent=0, context=context)
        if isinstance(encoded_root, list):
            lines.extend(encoded_root)
        else:
            lines.append(encoded_root)
        
    return "\n".join(lines)

def decode_tonl(text: str) -> Any:
    """
    Generic decoder for TONL format to Python objects.
    """
    parser = TonlParser(text)
    return parser.parse()

def calculate_token_savings(data: Any) -> TonlEncodeResult:
    json_text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    tonl_text = encode_tonl(data)
    
    j_len = len(json_text)
    t_len = len(tonl_text)
    savings = (1 - (t_len / j_len)) * 100 if j_len > 0 else 0.0
    
    return TonlEncodeResult(
        text=tonl_text,
        json_chars=j_len,
        tonl_chars=t_len,
        savings_percent=savings
    )

# --- Compatibility Wrappers ---

def encode_news_articles(articles: List[Dict], remove_url_to_image: bool = True) -> str:
    normalized = []
    for item in articles:
        norm = item.copy()
        if remove_url_to_image and "urlToImage" in norm:
            del norm["urlToImage"]
        
        src = item.get("source")
        if isinstance(src, dict):
            norm["source"] = src.get("name", "")
        elif src is None:
            norm["source"] = ""
        else:
            norm["source"] = str(src)
            
        if "publishedAt" in norm:
             norm["published_at"] = norm.pop("publishedAt")
             
        normalized.append(norm)
        
    return encode_tonl(normalized, root_key="news")

def decode_news_articles(tonl_text: str) -> List[Dict]:
    decoded = decode_tonl(tonl_text)
    if isinstance(decoded, dict) and "news" in decoded:
        return decoded["news"]
    elif isinstance(decoded, list):
        return decoded
    # Flattened root case: if decoded is a dict with keys like '0', '1'... it might be a list?
    # No, generic decoder returns dict. If news was top level, it returns {news: [...]}.
    # If flattened, it returns {0: ..., 1: ...} ? No, encode_tonl for list root uses "root_key" wrapper manually if not dict.
    # Wait, encode_news_articles wraps in "news" key if using encode_tonl(normalized, root_key="news")?
    # No, encode_tonl logic: if data is list (not dict), it wraps in root_key.
    # So { "news": [...] } structure.
    # But if data was passed as a dict { "news": [...] }, it would flatten.
    return decoded.get("news", decoded)

# --- Encoder Helpers ---

def _choose_best_delimiter(data: Any) -> str:
    # Heuristic: User prefers Pipe '|' for visual structure.
    # We will use '|' unless it causes too many collisions compared to others, 
    # but for consistent visuals, defaulting to '|' is often best even if some fields get quoted.
    
    # Check frequency?
    s_rep = str(data)
    pipe_count = s_rep.count("|")
    tab_count = s_rep.count("\t")
    
    # If pipes are rare or non-existent, use pipe.
    if pipe_count == 0: return "|"
    
    # If pipes are common but tabs are clean, use tab?
    # User complained about tab visuals. So let's stick to pipe unless it's a disaster.
    # Actually, strict TONL 2.0 doc encourages finding the "best" one to avoid quotes.
    # But for "table look", pipe is king. 
    # Let's return pipe. The encoder handles quoting automatically if delimiter is present in value.
    return "|"

def _encode_value(value: Any, key: str, indent: int, context: Dict) -> Union[str, List[str]]:
    prefix = f"{' ' * indent}{key}"
    
    if value is None:
        return f"{prefix}: null"
        
    if isinstance(value, bool):
        return f"{prefix}: {str(value).lower()}"
        
    if isinstance(value, (int, float)):
        return f"{prefix}: {value}"
        
    if isinstance(value, str):
        return f"{prefix}: {_quote_string(value, context['delimiter'])}"
        
    if isinstance(value, list):
        return _encode_array(value, key, indent, context)
        
    if isinstance(value, dict):
        return _encode_object(value, key, indent, context)
        
    return f"{prefix}: {_quote_string(str(value), context['delimiter'])}"

def _quote_string(text: str, delimiter: str) -> str:
    # 1. Multiline check
    if "\n" in text or "\r" in text:
        # Triple quote
        # Escape triple quotes inside
        escaped = text.replace('"""', '\\"""')
        return f'"""{escaped}"""'
        
    # 2. Delimiter check & special chars
    special_chars = {delimiter, ":", "{", "}", "[", "]", "#", "\"", "'"}
    
    # Needs quotes if: contains special char, leading/trailing space, empty, or reserved literal
    needs_quotes = (
        any(c in text for c in special_chars) or 
        text.strip() != text or 
        text == "" or 
        text in RESERVED_LITERALS or
        NUMBER_RE.match(text)
    )
    
    if needs_quotes:
        escaped = text.replace('"', '""')
        return f'"{escaped}"'
    
    return text

def _encode_array(arr: List[Any], key: str, indent: int, context: Dict) -> Union[str, List[str]]:
    if not arr:
        return f"{' ' * indent}{key}[0]:"

    if _is_uniform_object_array(arr):
        return _encode_tabular_array(arr, key, indent, context)

    # Primitive Array
    if all(not isinstance(x, (dict, list)) for x in arr):
        # Allow single line
        values = []
        for x in arr:
            # For arrays, we just use _value_to_string concept but simpler 
            # Note: _encode_value includes key prefix, we just want value string
            if x is None: v = "null"
            elif isinstance(x, bool): v = str(x).lower()
            elif isinstance(x, (int, float)): v = str(x)
            else: v = _quote_string(str(x), context['delimiter'])
            values.append(v)
            
        delimiter = context['delimiter']
        # Tab char usually needs escape in code if strictly following visual, but for parsing raw char is fine?
        # If delimiter is \t, we output literal tab.
        sep = delimiter + " " if delimiter != "\t" else "\t"
        joined = sep.join(values)
        
        header = f"{' ' * indent}{key}[{len(arr)}]:"
        if len(joined) + len(header) < 120 and "\n" not in joined:
             return f"{header} {joined}"
        
        # Multiline primitive array? Spec Example 3.1
        # It indents values.
        return [header, f"{' ' * (indent + context['indent_step'])}{joined}"]

    # Mixed Array
    lines = [f"{' ' * indent}{key}[{len(arr)}]:"]
    for i, item in enumerate(arr):
        item_encoded = _encode_value(item, f"[{i}]", indent + context["indent_step"], context)
        if isinstance(item_encoded, list):
            lines.extend(item_encoded)
        else:
            lines.append(item_encoded)
    return lines

def _encode_tabular_array(arr: List[Dict], key: str, indent: int, context: Dict) -> List[str]:
    # Preserve key order
    cols = list(arr[0].keys())
    col_str = ",".join(cols) # Spec uses commas in definition usually, or matches delimiter? Spec says "COLUMN_LIST = COLUMN (',' COLUMN)*", so definition uses comma always.
    
    header = f"{' ' * indent}{key}[{len(arr)}]{{{col_str}}}:"
    lines = [header]
    sub_indent = " " * (indent + context["indent_step"])
    delimiter = context['delimiter']
    sep = delimiter + " " if delimiter != "\t" else "\t"

    for item in arr:
        row_vals = []
        for col in cols:
            val = item.get(col)
            if val is None: v = "null"
            elif isinstance(val, bool): v = str(val).lower()
            elif isinstance(val, (int, float)): v = str(val)
            else: v = _quote_string(str(val), delimiter)
            row_vals.append(v)
        lines.append(f"{sub_indent}{sep.join(row_vals)}")
    return lines

def _encode_object(obj: Dict, key: str, indent: int, context: Dict) -> Union[str, List[str]]:
    if not obj:
        return f"{' ' * indent}{key}: {{}}"

    is_simple = all(not isinstance(v, (dict, list)) for v in obj.values())
    sorted_keys = list(obj.keys())
    col_str = ",".join(sorted_keys)
    header = f"{' ' * indent}{key}{{{col_str}}}:"

    if is_simple:
        parts = []
        for k in sorted_keys:
            val = obj[k]
            # Manual inline value encoding
            if val is None: v = "null"
            elif isinstance(val, bool): v = str(val).lower()
            elif isinstance(val, (int, float)): v = str(val)
            else: v = _quote_string(str(val), context['delimiter'])
            parts.append(f"{k}: {v}")
        joined = " ".join(parts)
        if len(header) + len(joined) < 120 and "\n" not in joined:
            return f"{header} {joined}"

    lines = [header]
    for k in sorted_keys:
        val_encoded = _encode_value(obj[k], k, indent + context["indent_step"], context)
        if isinstance(val_encoded, list):
            lines.extend(val_encoded)
        else:
            lines.append(val_encoded)
    return lines

def _is_uniform_object_array(arr: List[Any]) -> bool:
    if not arr or not isinstance(arr[0], dict): return False
    keys = set(arr[0].keys())
    for item in arr[1:]:
        if not isinstance(item, dict) or set(item.keys()) != keys: return False
    for item in arr:
        for v in item.values():
            if isinstance(v, (dict, list)): return False # Nested complex types break generic simple CSV tabular
    return True

# --- Decoder Implementation ---

class TonlParser:
    def __init__(self, text: str):
        self.text = text
        self.lines = text.splitlines()
        self.num_lines = len(self.lines)
        self.line_idx = 0
        self.delimiter = "," # Default

    def parse(self) -> Any:
        # Pass 1: Check directives
        while self.line_idx < self.num_lines:
            line = self.lines[self.line_idx].strip()
            if not line:
                self.line_idx += 1
                continue
            if line.startswith("#delimiter"):
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    d = parts[1].strip()
                    if d == "\\t": self.delimiter = "\t"
                    else: self.delimiter = d
                self.line_idx += 1
            elif line.startswith("#"):
                self.line_idx += 1
            else:
                break
        
        # Parse Root matches
        # If root key is implicit (just properties), we parse block at indent 0
        # If text is empty, return {}
        if self.line_idx >= self.num_lines:
            return {}
            
        # We need to detect if the first real line is a single root Block OR multiple keys
        # The spec Example 1.1 "root{...}: ..." implies a single root block named 'root'.
        # But JSON translation often implies flattening.
        # Let's try to parse as a multiline object body (top level).
        return self._parse_multiline_object(parent_indent=-1)

    def _parse_block(self, indent_threshold: int) -> Tuple[str, Any]:
        # Reads the next block/key-value
        # Returns (key, value)
        if self.line_idx >= self.num_lines:
            return None, None

        line = self.lines[self.line_idx]
        stripped = line.strip()
        current_indent = len(line) - len(stripped)
        
        # Debug/Safety
        # Match Header
        match = HEADER_RE.match(stripped)
        if not match:
            # Fallback or weird line? Skip?
            self.line_idx += 1
            return "error", None

        key = match.group("key")
        count_str = match.group("count")
        cols_str = match.group("cols")
        rest = match.group("rest").strip()
        
        # Move past header line
        self.line_idx += 1
        
        # Note: If 'rest' is empty, value follows on next lines.
        # If 'rest' starts with """, it's a multiline string value, possibly spanning lines.
        
        # Multiline String Check for 'rest'
        if rest.startswith('"""'):
            # It is a scalar value (triple quoted string)
            val = self._parse_triple_quoted_string(rest)
            return key, val

        # Case 1: Tabular Array
        if count_str and cols_str:
            return key, self._parse_tabular_array(int(count_str), cols_str.split(","))
            
        # Case 2: Object nesting
        if cols_str and not count_str:
            if rest:
                # Inline object
                return key, self._parse_inline_object(rest)
            else:
                return key, self._parse_multiline_object(current_indent)

        # Case 3: Array (Mixed or Primitive)
        if count_str:
            if not rest:
                return key, self._parse_mixed_array(int(count_str), current_indent)
            else:
                return key, self._parse_inline_primitive_array(rest)
                
        # Case 4: Key-Value (Primitive or generic multiline object start)
        if rest:
            # "key: value"
            return key, self._parse_value_string(rest)
        else:
            # "key:"
            return key, self._parse_multiline_object(current_indent)
            
    def _parse_triple_quoted_string(self, first_line_rest: str) -> str:
        # first_line_rest starts with """
        # We need to find the closing """
        # It might be on the same line: """hello"""
        
        # Safety: check if it's strictly """...""" on one line
        # Regex for single line valid triple: ^"""(?!")(.*)"""$ ?
        # Or simple check:
        if len(first_line_rest) >= 6 and first_line_rest.endswith('"""') and not first_line_rest.endswith('\\"""'):
             # One liner
             content = first_line_rest[3:-3]
             return content.replace('\\"""', '"""')

        # Multi-line
        buffer = [first_line_rest[3:]] # content after first """
        
        while self.line_idx < self.num_lines:
            line = self.lines[self.line_idx]
            self.line_idx += 1
            
            # Check for end
            stripped = line.strip() 
            # Note: Closing """ could be anywhere, but generic formatter puts it at end?
            # Actually we just look for """ in the line.
            # But wait, indented multiline strings?
            # Spec says:
            #   code: """function hello() {
            #   return 'world';
            # }"""
            # The lines inside seem to preserve indentation relative to... what?
            # Usually strict YAML-like rules apply but here we just consume lines until """
            
            if line.strip().endswith('"""') and not line.strip().endswith('\\"""'):
                # Found end
                # careful with leading spaces? tonl typically preserves exact content inside """
                # if the user typed:
                # key: """
                #   line1
                # """
                # We usually want "  line1".
                end_idx = line.rfind('"""')
                buffer.append(line[:end_idx])
                full_text = "\n".join(buffer)
                return full_text.replace('\\"""', '"""')
            else:
                buffer.append(line)
                
        # EOF reached without closing
        return "\n".join(buffer)

    def _parse_multiline_object(self, parent_indent: int) -> Dict[str, Any]:
        obj = {}
        while self.line_idx < self.num_lines:
            # Peek
            line = self.lines[self.line_idx]
            stripped = line.strip()
            if not stripped: 
                self.line_idx += 1
                continue
                
            indent = len(line) - len(stripped)
            if indent <= parent_indent and parent_indent != -1:
                break
                
            k, v = self._parse_block(indent)
            if k is not None:
                obj[k] = v
            else:
                # Should not happen unless error/comment
                pass
                
        return obj

    def _parse_tabular_array(self, count: int, cols: List[str]) -> List[Dict]:
        items = []
        cols = [c.strip() for c in cols]
        
        # We need to parse exactly 'count' items.
        # But a single item might span multiple physical lines if it has """ strings.
        processed_items = 0
        
        while processed_items < count and self.line_idx < self.num_lines:
            # Start accumulating a logical row
            buffer = []
            
            # Read first line
            while self.line_idx < self.num_lines:
                line = self.lines[self.line_idx]
                # If it's a completely empty line between records, maybe skip?
                # But inside a multiline string, empty lines are significant.
                # If we haven't started buffering, we can skip blanks (unless it's null row?)
                if not buffer and not line.strip():
                    self.line_idx += 1
                    continue
                
                buffer.append(line)
                self.line_idx += 1
                
                # Check if the buffer currently forms a complete logical row
                # A logical row is complete if all triple quotes are balanced.
                # Actually, splitting by delimiter adds complexity.
                # Let's verify balance on the raw text first?
                # But delimiter can be inside quotes.
                
                # Robust approach: 
                # Attempt to split the CURRENT buffer contents as if it's one big line.
                # If the last token is an "unclosed string", we need more lines.
                
                # Join buffer with newlines to reconstruct the text block so far
                current_text = "\n".join(buffer) # Keep newlines
                
                if self._is_balanced(current_text):
                    # It's a valid row
                    break
                # Else: continue loop to append next line
            
            if not buffer:
                break # EOF
                
            # Now we have a full logical row text. Split it.
            logical_line = "\n".join(buffer) # This might have indent?
            # Usually strict tabular lines start with indent. Buffer has raw lines.
            
            # We need to be careful: the indentation of the first line belongs to the structure,
            # but subsequent lines might be part of the multiline string content.
            # However, split_delimiter parses the string values.
            
            vals = self._split_delimiter(logical_line)
            item = {}
            for i, col in enumerate(cols):
                v_str = vals[i] if i < len(vals) else "null"
                item[col] = self._parse_value_string(v_str)
            items.append(item)
            processed_items += 1
            
        return items

    def _is_balanced(self, text: str) -> bool:
        # Check if quotes are balanced.
        # Simple heuristic: Count triple quotes """ ?
        # "key": """value""" -> 2 occurrences.
        # "key": """val \n ue""" -> 2 occurrences.
        # "key": """val""" | """val2""" -> 4 occurrences.
        # So count of """ must be even?
        # What if """ is inside a normal string? "a \"\"\" b" -> escaped?
        # Or if " is inside """ ?
        
        # A proper state machine is needed just like _split_delimiter but just returning status.
        # Let's reuse _split_delimiter logic but return success flag?
        # No, _split_delimiter just splits.
        # Let's write a quick scanner.
        
        pos = 0
        length = len(text)
        in_quote = False
        quote_style = None # '"' or '"""'
        
        while pos < length:
            # Check for Triple Quote
            if text.startswith('"""', pos) and (pos == 0 or text[pos-1] != '\\'):
                if in_quote:
                    if quote_style == '"""':
                        in_quote = False # Closed
                        quote_style = None
                        pos += 3
                        continue
                    # Else inside normal quote, ignore? " says """ " -> Valid.
                else:
                    in_quote = True
                    quote_style = '"""'
                    pos += 3
                    continue
            
            # Check for Single Quote (Double Quote char)
            elif text.startswith('"', pos) and (pos == 0 or text[pos-1] != '\\'):
                if in_quote:
                    if quote_style == '"':
                        in_quote = False
                        quote_style = None
                        pos += 1
                        continue
                else:
                    in_quote = True
                    quote_style = '"'
                    pos += 1
                    continue
            
            pos += 1
            
        return not in_quote

    def _parse_inline_primitive_array(self, content: str) -> List[Any]:
        vals = self._split_delimiter(content)
        return [self._parse_value_string(v) for v in vals]

    def _parse_mixed_array(self, count: int, parent_indent: int) -> List[Any]:
        items = [None] * count
        while self.line_idx < self.num_lines:
            line = self.lines[self.line_idx]
            indent = len(line) - len(line.strip())
            if indent <= parent_indent: break
            
            k, v = self._parse_block(indent)
            # k should be "[index]"
            if k.startswith("[") and k.endswith("]"):
                try:
                    idx = int(k[1:-1])
                    if 0 <= idx < count: items[idx] = v
                except: pass
            else:
                pass # ignore unknown keys in array block
        return items

    def _parse_inline_object(self, content: str) -> Dict[str, Any]:
        # Regex for "key: val"
        # Since we have delimiters like " language: en", split by spaces with key regex
        parts = re.split(r'\s+([a-zA-Z_]\w*):\s+', " " + content)
        obj = {}
        i = 1
        while i < len(parts) - 1:
            k = parts[i]
            v = parts[i+1]
            obj[k] = self._parse_value_string(v.strip())
            i += 2
        return obj

    def _parse_value_string(self, text: str) -> Any:
        text = text.strip()
        if text == "null": return None
        if text == "true": return True
        if text == "false": return False
        
        # Triple quote check (inline)
        if text.startswith('"""') and text.endswith('"""') and len(text) >= 6:
             return text[3:-3].replace('\\"""', '"""')
             
        # Double quote check
        if text.startswith('"') and text.endswith('"'):
            # replace "" -> "
            return text[1:-1].replace('""', '"')
            
        if NUMBER_RE.match(text):
            if "." in text or "e" in text.lower():
                return float(text)
            return int(text)
            
        return text

    def _split_delimiter(self, line: str) -> List[str]:
        # Split by self.delimiter but respect quotes
        # Simple state machine
        res = []
        cur = []
        in_quote = False
        i = 0
        d = self.delimiter
        l = len(line)
        while i < l:
            c = line[i]
            if c == '"':
                in_quote = not in_quote
                cur.append(c)
            elif c == d and not in_quote:
                res.append("".join(cur).strip())
                cur = []
            else:
                cur.append(c)
            i += 1
        res.append("".join(cur).strip())
        return res
