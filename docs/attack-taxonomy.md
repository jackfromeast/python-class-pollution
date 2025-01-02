## Attack Taxonomy

The Class Pollution vulnerability aligns with CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes, also known as "Mass Assignment." This CWE category serves as the parent of CWE-1321: Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution'). The distinction lies in that CWE-1321 specifically allows overwriting parent objects whose attributes are shared across other runtime objects, thereby affecting a broader scope.

To better understand the prevalence and impact of Class Pollution vulnerabilities, we propose the first comprehensive taxonomy of Class Pollution attacks, systematically categorizing them based on their scope of impact.

![taxonomy](./assets/attack-taxonomy.jpg)

### 1/ Field-only Pollution

In a field-only pollution attack, an attacker can overwrite arbitrary fields within a given base object of type MutableMapping. This can result in security issues such as privilege escalation if the base dictionary contains privilege-related fields that should not be modified by the user. However, the impact of this type of pollution is limited to the targeted base object and does not extend to other objects within the runtime environment (the fields are not shared between different object directly).

The root cause of this vulnerability lies in excessive privileges being granted to the user, allowing unauthorized modification of sensitive fields.

#### PoC

The following functions demonstrate how field-only pollution can occur at both single and multi-levels in a dictionary-like structure:

```
from typing import Dict

# Single-level field-only pollution
def single_level_field_only_pollution_func(base: Dict, input: Dict) -> Dict:
    """
    Overwrites fields in the base dictionary with values from the input dictionary.
    This allows modification of any key-value pairs directly within the base object.
    """
    for key, val in input.items():
      base[key] = val
    return base

# Multi-level field-only pollution
def multi_level_field_only_pollution_func(base: Dict, input: Dict) -> Dict:
  """
  Recursively overwrites fields in a nested dictionary structure.
  If a field in the base dictionary is itself a dictionary, the function
  continues to overwrite fields at deeper levels.
  """
  for key, val in input.items():
    if isinstance(base.get(key), dict):  # Ensure the value is a dictionary
      base[key] = multi_level_field_only_pollution_func(base[key], val)
    else:
      base[key] = val  # Overwrite field if not a dictionary
  return base
```

#### Real-World Cases

TODO: Fill this will a zero-day. I didn't find a CVE for this type of pollution actually (using `obj[key]` or `obj.update`). 

+ https://knowledge-base.secureflag.com/vulnerabilities/inadequate_input_validation/mass_assignment_python.html

```
@object.route("/insert", methods=['POST'])
def object_insert():
    # initialise the dictionary with a predefined value
    values = {'isAdmin': get_admin_status()}

    # update the values (sensitive_field may be overridden)
    values.update(request.form.to_dict(flat=True))

    # pass the dictionary to the SQL query
    sql_statement = 'INSERT INTO messages VALUES (:isAdmin, :values_from_user)'
    conn = sqlite3.connect('db.sqlite')
    conn.cursor().execute(sql_statement, values)
    conn.commit()
    return redirect("/", code=201)
```

### 2/ Single-level Attribute-only Pollution

In a single-level attribute-only pollution attack, an attacker can overwrite arbitrary attributes, including special dunder (double underscore) attributes, of a given base object. Similar to field-only pollution, this can lead to security issues such as privilege escalation. Additionally, overwriting function attributes with attacker-controlled string values can result in a denial-of-service (DoS) condition. However, the impact of this type of pollution is limited to the targeted base object, as the attributes are not directly shared between different objects within the runtime environment.

#### PoC

```
from typing import Dict

# Single-level attribute-only pollution
def single_level_attr_only_pollution_func(base: object, input: Dict) -> object:
    """
    Overwrites attributes of the base object with key-value pairs from the input dictionary.
    This allows arbitrary modifications, including potential overwrites of dunder attributes.
    """
    for key, val in input.items():
        setattr(base, key, val)  # Set or overwrite the attribute on the base object
    return base
```

#### Real-World Cases

+ CVE-2024-7297: Langflow Privilege Escalation through Mass Assignment
  + Reference: https://www.tenable.com/security/research/tra-2024-26

```
async def update_user(user_db: User | None, user: UserUpdate, db: AsyncSession) -> User:
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    # user_db_by_username = get_user_by_username(db, user.username)
    # if user_db_by_username and user_db_by_username.id != user_id:
    #     raise HTTPException(status_code=409, detail="Username already exists")

    user_data = user.model_dump(exclude_unset=True)
    changed = False
    for attr, value in user_data.items():
        if hasattr(user_db, attr) and value is not None:
            setattr(user_db, attr, value)
            changed = True
```


### 3/ Multi-level Attribute-only Pollution

In a multi-level attribute-only pollution attack, an attacker can recursively overwrite arbitrary attributes starting from a given base object. This type of attack is significantly more powerful because it allows the attacker to modify attributes of other objects or classes, provided they can be accessed through a chain of getattr operations starting from the base object.

Such attacks can lead to denial-of-service (DoS) and potentially more severe consequences if exploitable gadgets exist in the affected attributes. However, this attack is inherently limited in scope—it cannot overwrite global variables stored in a module's global scope (accessible via a function’s `__globals__` attribute), as the global scope is essentially a dictionary that its fields cannot be traversed using `getattr`.


#### PoC

```
from typing import Dict

def multi_level_attr_only_pollution_func(base: object, input: Dict) -> object:
    """
    Recursively overwrites attributes of the base object with key-value pairs from the input dictionary.
    If an attribute's value is itself a dictionary, the function recursively traverses and modifies it.
    """
    for key, val in input.items():
        if isinstance(val, dict) and hasattr(base, key):
            nested_base = getattr(base, key)
            setattr(base, key, multi_level_attr_only_pollution_func(nested_base, val))
        else:
            setattr(base, key, val)
    
    return base
```

#### Real-World Cases

TODO: Fill me with a zero-day vulnerability.

### 4/ Multi-level Pollution

A multi-level pollution attack enables an attacker to recursively overwrite arbitrary attributes or fields starting from a given base object. Unlike multi-level attribute-only pollution, this type of attack is more versatile as it can overwrite both fields (dictionary-like objects) and attributes (object properties), depending on the type of the object being targeted.

This distinction is crucial because, in the case of multi-level pollution, attackers can potentially pollute values within the global scope of a module. This is achievable by exploiting attributes such as `obj.__class__.__init__.__globals__[key]`, which grants access to and allows modification of global variables.

#### PoC

```
def multi_level_pollution_func(base: object, input: Dict) -> object:
  for k, v in input.items():
      if hasattr(dst, '__getitem__'):
          if base.get(k) and type(v) == dict:
              multi_level_attr_only_pollution_func(v, base.get(k))
          else:
              base[k] = v
      elif hasattr(base, k) and type(v) == dict:
          multi_level_attr_only_pollution_func(v, getattr(base, k))
      else:
          setattr(base, k, v)
```


#### PoC

+ Mesop Case

```
def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
  for key, value in json_dict.items():
    if hasattr(instance, key):
      attr = getattr(instance, key)
      if isinstance(value, dict):
        # If the value is a dict, recursively update the dataclass.
        setattr(
          instance,
          key,
          _recursive_update_dataclass_from_json_obj(attr, value),
        )
      ...
      else:
        # For other types, set the value directly.
        setattr(instance, key, value)
    else:
      if isinstance(instance, dict):
        instance[key] = value
      else:
        raise MesopException(
          f"Unhandled stateclass deserialization where key={key}, value={value}, instance={instance}"
        )
  return instance
```