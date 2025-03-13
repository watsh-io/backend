from watsh.lib.exceptions import InvalidKeyPathError
from src.watsh.lib.key import get_key, delete_key, set_key


# Tests
d = {
    "foo": {"bar": "baz"},
    "alpha": [
        "beta",
        "charlie"
    ],
}

assert get_key(d, "foo.bar") == "baz"
assert get_key(d, "alpha.0") == "beta"

set_key(d, "foo.bar", "test")
print(d)
assert get_key(d, "foo.bar") == "test"

set_key(d, "alpha.0", "test")
print(d)
assert get_key(d, "alpha.0") == "test"

set_key(d, "foo.baz", "test")
print(d)
assert get_key(d, "foo.baz") == "test"

set_key(d, "alpha.2", "delta")
print(d)
assert get_key(d, "alpha.2") == "delta"

delete_key(d, "foo.baz")
print(d)
try:
    get_key(d, "foo.baz")
except InvalidKeyPathError as e:
    pass

delete_key(d, "alpha.0")
print(d)
assert get_key(d, "alpha.0") == "charlie"

try:
    get_key(d, "alpha.1")
except InvalidKeyPathError as e:
    pass
try:
    get_key(d, "alpha.2")
except InvalidKeyPathError as e:
    pass

delete_key(d, "alpha.1")
print(d)

set_key(d, "alpha.3", {"name": "echo"})
print(d)
assert get_key(d, "alpha.3.name") == "echo"

delete_key(d, "alpha.3.name")
print(d)
try:
    get_key(d, "alpha.3.name")
except InvalidKeyPathError as e:
    pass

set_key(d, "alpha.-1", {"name": "foxtrot"})
print(d)
assert get_key(d, "alpha.-1.name") == "foxtrot"

# Test for appending an object at the end of the list
set_key(d, "alpha.-1", {"name": "golf"})
print(d)
assert get_key(d, "alpha.-1.name") == "golf"

# Deleting the appended object
delete_key(d, "alpha.-1.name")
print(d)
try:
    get_key(d, "alpha.-1.name")
except InvalidKeyPathError as e:
    pass


# Additional Tests
d = {
    "foo": {"bar": "baz"},
    "alpha": [
        {"name": "beta"},
        {"name": "charlie"}
    ],
}

# Test for deleting all elements in the list with wildcard
delete_key(d, "alpha.*")
print(d)
assert get_key(d, "alpha") == []

# Test for deleting all elements in the list of dictionaries
delete_key(d, "alpha.*.name")
print(d)
assert get_key(d, "alpha") == []

# Test for deleting a specific key in all dictionaries in the list
delete_key(d, "alpha.*.age")
print(d)
assert get_key(d, "alpha") == []

# Test for deleting a specific key in all dictionaries in the list, including nested dictionaries
set_key(d, "alpha", [{"name": "delta", "age": 25}, {"name": "echo", "age": 30, "info": {"gender": "male"}}])
delete_key(d, "alpha.*.info.gender")
print(d)
assert get_key(d, "alpha.*.info") == [None, {}]

# Test for invalid key path
try:
    get_key(d, "alpha.*.info.invalid")
except InvalidKeyPathError as e:
    pass


data = {
    "foo": [
        {"bar": True},
    ]
}

# Add {"baz": True} to foo.1
set_key(data, "foo.1", {"baz": True})
print(data)
assert get_key(data, "foo.1") == {"baz": True}

# Delete foo.0
delete_key(data, "foo.0")
print(data)
assert get_key(data, "foo.0") == {"baz": True}

print("All tests passed successfully!")
