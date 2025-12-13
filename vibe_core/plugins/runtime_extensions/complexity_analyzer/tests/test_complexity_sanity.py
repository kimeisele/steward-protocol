import os
import tempfile

from vibe_core.plugins.runtime_extensions.complexity_analyzer.plugin_main import ComplexityAnalyzerPlugin


def test_complexity_analyzer_instantiation():
    plugin = ComplexityAnalyzerPlugin()
    assert plugin.plugin_id == "complexity_analyzer"


def test_analyze_complexity():
    plugin = ComplexityAnalyzerPlugin()

    # Create a temporary python file
    content = """
def simple():
    return 1

def complex_func(x):
    if x > 0:
        for i in range(x):
            print(i)
    else:
        return 0
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = plugin._handle_analyze_complexity(None, {"file_path": tmp_path})
        assert result["success"] is True
        assert result["total_complexity"] > 0

        funcs = result["function_complexity"]
        assert "simple" in funcs
        assert "complex_func" in funcs
        assert funcs["complex_func"] > funcs["simple"]

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
