import os

folders = os.listdir("server/output")
count = 0
for f in folders:
    fold = "/home/grads/hadiamjad/repositories/speed-graph/server/output/" + f + "/graph.pdf"
    if os.path.exists(fold):
        count += 1
print(count)