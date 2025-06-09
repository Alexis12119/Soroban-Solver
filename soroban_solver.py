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
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+-*/÷'
        data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
        print("OCR Data: ", data)
        
        # Enhanced text processing with spatial awareness
        text_elements = self._process_ocr_data(data)
        
        # Get bounding boxes for detected text
        boxes = []
        for i, word in enumerate(data['text']):
            if word.strip():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                boxes.append((x, y, x + w, y + h))

        # Parse mathematical expression with spatial context
        operation, numbers = self._parse_mathematical_expression_enhanced(text_elements)
        
        # Combine all text for backward compatibility
        combined_text = " ".join([elem['text'] for elem in text_elements])
        
        return operation, numbers, combined_text.strip(), boxes

    def _process_ocr_data(self, data):
        """Process OCR data with spatial awareness"""
        text_elements = []
        
        for i, text in enumerate(data['text']):
            if text.strip():
                raw = text.strip()
# Normalize common OCR confusions
                cleaned_text = (raw.replace('O', '0')
                                   .replace('o', '0')
                                   .replace('l', '1')
                                   .replace('I', '1')
                                   .replace('×', '*')
                                   .replace('x', '*')
                                   .replace('−', '-')
                                   .replace('–', '-')
                                   .replace('|', '1')
                                   .replace('÷', '/')
                                   .replace(':', '/'))

# Extra pass: if it's a '+' but surrounded by numbers, assume it's a mistaken division
                if raw == '+' or cleaned_text == '+':
                    idx = i
                    left_ok = idx > 0 and data['text'][idx - 1].strip().isdigit()
                    right_ok = idx < len(data['text']) - 1 and data['text'][idx + 1].strip().isdigit()
                    if left_ok and right_ok:
                        print(f"Correcting misread '+' to '/' at index {idx}")
                        cleaned_text = '/'
                element = {
                    'text': cleaned_text,
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': int(data['conf'][i])
                }

                # 🧼 Filter: Skip elements in top-left corner (likely back/menu buttons)
                if self._is_ui_element(element):
                    print(f"Skipping potential UI element: '{element['text']}' at ({element['x']}, {element['y']})")
                    continue
                
                text_elements.append(element)
        
        # Sort by x-coordinate (left to right) for proper reading order
        text_elements.sort(key=lambda x: x['x'])
        
        return text_elements

    def _is_ui_element(self, element, ui_corner_size=150):
        """Check if element is in a typical UI corner (e.g. back button area)"""
        return element['x'] < ui_corner_size and element['y'] < ui_corner_size

    def _parse_mathematical_expression_enhanced(self, text_elements):
        """Enhanced parsing that considers spatial layout and filters false positives"""
        if not text_elements:
            return None, None
        
        # Filter out low-confidence single digits that might be false positives
        filtered_elements = []
        for element in text_elements:
            text = element['text']
            confidence = element['confidence']
            # Skip single digits with low confidence (likely false positives)
            if (len(text) == 1 and text.isdigit() and confidence < 70):
                print(f"Filtering out low-confidence single digit: '{text}' (confidence: {confidence})")
                continue
            
            # Skip very short text with very low confidence
            if len(text) <= 2 and confidence < 60:
                print(f"Filtering out low-confidence short text: '{text}' (confidence: {confidence})")
                continue
                
            filtered_elements.append(element)
        
        # Strategy 1: Look for the main mathematical expression (longest text with operators)
        main_expression = None
        best_candidate = None
        
        for element in filtered_elements:
            text = element['text']
            # Check if this element contains mathematical operators
            if re.search(r'[+\-×x*/÷]', text):
                if main_expression is None or len(text) > len(main_expression):
                    main_expression = text
                    best_candidate = element
        
        # If we found a main expression, parse it
        if main_expression:
            print(f"Using main expression: '{main_expression}' (confidence: {best_candidate['confidence']})")
            return self._parse_single_expression(main_expression)
        
        # Strategy 2: Combine remaining high-confidence text and try to parse
        high_conf_text = [elem['text'] for elem in filtered_elements if elem['confidence'] > 50]
        if high_conf_text:
            combined_text = " ".join(high_conf_text)
            print(f"Using combined high-confidence text: '{combined_text}'")
            return self._parse_single_expression(combined_text)
        
        # Strategy 3: Last resort - use all remaining text
        combined_text = " ".join([elem['text'] for elem in filtered_elements])
        return self._parse_single_expression(combined_text)

    def _parse_single_expression(self, text):
        """Parse a single mathematical expression"""
        cleaned = text.replace('×', '*').replace('x', '*').replace('−', '-').replace('÷', '/')

        # Try parsing full expression first
        expr = "".join(re.findall(r'[\d\.\+\-\*/\(\)]', cleaned))
        if expr and re.fullmatch(r'[\d\.\+\-\*/\(\) ]+', expr):
            return 'expression', expr

        # If full expression fails, fallback to binary operator matching
        binary_ops = [
            (r'(\d+\.?\d*)\s*[/÷:]\s*(\d+\.?\d*)', 'division'),
            (r'(\d+\.?\d*)\s*[\+\−-]\s*(\d+\.?\d*)', 'addition'),
            (r'(\d+\.?\d*)\s*[*×x]\s*(\d+\.?\d*)', 'multiplication'),
            (r'(\d+\.?\d*)\s*[\-−]\s*(\d+\.?\d*)', 'subtraction'),
        ]
        for pattern, op_type in binary_ops:
            match = re.search(pattern, cleaned)
            if match:
                nums = [float(match.group(1)), float(match.group(2))]
                return op_type, nums

        return None, None

    def _parse_mathematical_expression(self, text):
        """Legacy method - kept for backward compatibility"""
        return self._parse_single_expression(text)

    def is_valid_equation_window(self, image, raw_text):
        """Enhanced validation to check if we're looking at a valid equation window"""
        
        # Check: Text should be mostly mathematical
        math_chars = sum(1 for c in raw_text if c.isdigit() or c in '+-*/=().')
        total_chars = len(raw_text.replace(' ', ''))
        if total_chars > 0:
            math_ratio = math_chars / total_chars
            if math_ratio < 0.6:  # At least 60% should be math-related
                return False
        
        # Check: Look for common non-equation indicators
        if self._contains_non_equation_text(raw_text):
            return False
        
        # Check: Must contain at least one mathematical operator
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
                print(f"Evaluating expression: {numbers!r}")
                result = eval(numbers, {"__builtins__": None}, {})
                # Round floats sensibly
                if isinstance(result, float) and not result.is_integer():
                    return round(result, 4)
                return int(result) if isinstance(result, float) and result.is_integer() else result

            elif operation == 'division':
                result = numbers[0] / numbers[1]
                # Round to reasonable precision for division
                print("Result: ", result)
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
