import os

os.system("""ssh -i \.ssh\numen_collector_ssh root@215.16.144.120 -p 1257 "export PATH=\"/usr/bin:/usr/local/bin:/sbin:/bin\" && python EgressTestV2.py" """)