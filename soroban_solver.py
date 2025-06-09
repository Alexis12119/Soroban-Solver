import pytesseract
import re


class SorobanSolver:
    def __init__(self):
        pass

    def extract_problem_from_soroban(self, image, threshold=100):
        """Extract mathematical problem from soroban app screen"""
        width, height = image.size
        cropped = image.crop((0, 0, width, height // 4))

        # Convert to grayscale and binarize with dynamic threshold
        gray = cropped.convert('L').point(lambda x: 255 if x > threshold else 0, '1')

        # Get OCR data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Clean OCR text: Remove common OCR confusions
        cleaned_words = []
        for w in data['text']:
            if w.strip():
                w = (w.replace('O', '0')
                       .replace('o', '0')
                       .replace('l', '1')
                       .replace('I', '1')
                       .replace('÷', '/')
                       .replace(':', '/')
                       .replace('x', '*')
                       .replace('×', '*')
                       .replace('−', '-')
                       .replace('–', '-')
                       .replace('|', '1')
                       .replace('“', '"')
                       .replace('”', '"'))
                cleaned_words.append(w)
        text = " ".join(cleaned_words)

        # Get bounding boxes for detected text
        boxes = []
        for i, word in enumerate(data['text']):
            if word.strip():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                boxes.append((x, y, x + w, y + h))

        # Parse mathematical expression
        operation, numbers = self._parse_mathematical_expression(text)
        
        return operation, numbers, text.strip(), boxes

    def _parse_mathematical_expression(self, text):
        """Parse mathematical expression from OCR text"""
        cleaned = text.replace('×', '*').replace('x', '*').replace('−', '-').replace('÷', '/')

        # Try parsing full expression first
        expr = "".join(re.findall(r'[\d\.\+\-\*/\(\)]', cleaned))
        if expr and re.fullmatch(r'[\d\.\+\-\*/\(\) ]+', expr):
            return 'expression', expr

        # If full expression fails, fallback to binary operator matching
        binary_ops = [
            (r'(\d+\.?\d*)\s*[/÷]\s*(\d+\.?\d*)', 'division'),
            (r'(\d+\.?\d*)\s*[\+\−-]\s*(\d+\.?\d*)', 'addition'),  # will handle both + and −
            (r'(\d+\.?\d*)\s*[*×x]\s*(\d+\.?\d*)', 'multiplication'),
        ]
        for pattern, op_type in binary_ops:
            match = re.search(pattern, cleaned)
            if match:
                nums = [float(match.group(1)), float(match.group(2))]
                return op_type, nums

        return None, None

    def is_valid_equation_window(self, image, raw_text):
        """Enhanced validation to check if we're looking at a valid equation window"""
        
        # Check 2: Text should be mostly mathematical
        math_chars = sum(1 for c in raw_text if c.isdigit() or c in '+-*/=().')
        total_chars = len(raw_text.replace(' ', ''))
        if total_chars > 0:
            math_ratio = math_chars / total_chars
            if math_ratio < 0.6:  # At least 60% should be math-related
                return False
        
        # Check 3: Look for common non-equation indicators
        if self._contains_non_equation_text(raw_text):
            return False
        
        
        if not re.search(r'[+\-×x*/÷]', raw_text):
            return False
                
        return True

    def _contains_non_equation_text(self, raw_text):
        """Check if text contains non-equation indicators"""
        invalid_patterns = [
            r'challenge', r'level', r'score', r'time', r'menu', 
            r'start', r'pause', r'resume', r'home', r'settings'
        ]
        text_lower = raw_text.lower()
        for pattern in invalid_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def calculate_result(self, operation, numbers):
        """Calculate the result of the mathematical operation"""
        try:
            if operation == 'expression':
                result = eval(numbers, {"__builtins__": None}, {})
                # Round floats sensibly
                if isinstance(result, float) and not result.is_integer():
                    return round(result, 4)
                return int(result) if isinstance(result, float) and result.is_integer() else result

            elif operation == 'division':
                result = numbers[0] / numbers[1]
                # Round to reasonable precision for division
                if result.is_integer():
                    return int(result)
                return round(result, 4)
            
            elif operation == 'addition':
                return numbers[0] + numbers[1]
            
            elif operation == 'subtraction':
                return numbers[0] - numbers[1]
            
            elif operation == 'multiplication':
                return numbers[0] * numbers[1]
                
        except Exception as e:
            print(f"Calculation error: {e}")
            return None
        return None
