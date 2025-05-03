pip install build twine

python3 -m build

# if TEST_PYPI = true
if [ "$TEST_PYPI" = true ]; then
    echo "Publishing to Test PyPI..."
    python3 -m twine upload --repository testpypi dist/*
else
    echo "Publishing to PyPI..."
    python3 -m twine upload dist/*
fi