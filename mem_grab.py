import pymem
import pymem.process

pm = pymem.Pymem('halo5forge.exe')
base = pymem.process.module_from_name(pm.process_handle, 'halo5forge.exe').lpBaseOfDll

yaddr1 = base + int("6149FDC", 16)
yaddr2 = base + int("614A044", 16)
yaddr3 = base + int("614A078", 16)

ypos = pm.read_float(yaddr1)

xaddr1 = base + int("6149FD4", 16)
xaddr2 = base + int("614A03C", 16)
xaddr3 = base + int("614A070", 16)

xpos = pm.read_float(xaddr1)

zaddr1 = base + int("614A110", 16)
zaddr2 = base + int("61AFA94", 16)
zaddr3 = base + int("61AFBCC", 16)
zaddr4 = base + int("61AFC9C", 16)

zpos = pm.read_float(zaddr1)

print(f"X: {xpos}")
print(f"Y: {ypos}")
print(f"Z: {zpos}")