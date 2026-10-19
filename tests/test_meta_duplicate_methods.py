import ast
import glob

ALLOWLIST = [
    # format: "filepath::Class1|Class2::method_name"
]

def test_meta_no_duplicate_methods_in_classes():
    offenders = []

    for filepath in glob.glob("tests/test_*.py"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
        class_methods = {}

        for cls in classes:
            methods = {}
            for item in cls.body:
                if isinstance(item, ast.FunctionDef):
                    dumped = [ast.dump(stmt, include_attributes=False) for stmt in item.body]
                    methods[item.name] = dumped
            class_methods[cls.name] = methods

        cls_names = list(class_methods.keys())
        for i in range(len(cls_names)):
            for j in range(i + 1, len(cls_names)):
                cls1 = cls_names[i]
                cls2 = cls_names[j]
                methods1 = class_methods[cls1]
                methods2 = class_methods[cls2]

                for mname in set(methods1.keys()).intersection(set(methods2.keys())):
                    if methods1[mname] == methods2[mname]:
                        offender = f"{filepath}::{cls1}|{cls2}::{mname}"
                        offender2 = f"{filepath}::{cls2}|{cls1}::{mname}"
                        if offender not in ALLOWLIST and offender2 not in ALLOWLIST:
                            offenders.append(offender)

    assert not offenders, f"Duplicate identical methods found in different classes in the same file:\n" + "\n".join(offenders)
