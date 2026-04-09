import sys

from app.utils import clean_text

def test_clean_text_removes_html():
    html = "<div>Hello <b>World</b></div>"
    assert clean_text(html) == "Hello World"

def test_clean_text_removes_urls():
    text = "Visit https://google.com for more"
    assert clean_text(text) == "Visit for more"

def test_clean_text_preserves_technical_chars():
    text = "Skills: C++, C#, .NET"
    # The current clean_text logic removes : and ,
    assert clean_text(text) == "Skills C++ C# .NET"

def test_clean_text_trims_and_fixes_spacing():
    text = "  Too    many   spaces   "
    assert clean_text(text) == "Too many spaces"

if __name__ == "__main__":
    print("Running tests...")
    try:
        test_clean_text_removes_html()
        test_clean_text_removes_urls()
        test_clean_text_preserves_technical_chars()
        test_clean_text_trims_and_fixes_spacing()
        print("DONE: All utils tests passed!")
    except AssertionError as e:
        print(f"FAIL: Test failed")
        sys.exit(1)
