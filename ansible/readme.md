# Ansible

## TOC

* [Ansible](#ansible)
  * [TOC](#toc)
  * [Pre-requirements](#pre-requirements)
  * [Image building](#image-building)
  * [Image burn](#image-burn)
  * [NAS Part](#nas-part)
  * [Ansible part](#ansible-part)
  * [Helpful stuff](#helpful-stuff)
    * [Aliases](#aliases)
    * [Manually converting qcow2 to img](#manually-converting-qcow2-to-img)
    * [Existing ZFS pool](#existing-zfs-pool)
    * [Debug](#debug)

## Pre-requirements

Browse `vars/` folder and do necessary changes like:
  * `packer`:
    * `macaddress`
    * `authorized_keys`
    * `hostname`
    * `username`
    * `password`
  * `zfs`:
    * `zfs_pools`
    * `zfs_datasets`
    * `zfs_dataset_pass`

as well as:
  * `ansible.cfg`:
    * `remote_user`

## Image building

```bash
ansible-playbook packer.yml --ask-become-pass
```

then wait 30-40min and image should create itself via packer in `ansible/tmp/output`

## Image burn

To burn image to `/dev/disk5` (`disk5` used as example), type:

```bash
cd tmp/output

sudo su

#as sudo
pv -tpreb nas-ubuntu-server.img | dd of=/dev/disk5 bs=4096 conv=notrunc,noerror
```

## NAS Part

Before running new ubuntu server get all IP addresses in target network via `nmap`:

```bash
nmap -sP 10.0.0.0/24
# or
arp -a
```

Unplug USB from PC and plug into NAS (no matter which USB port).

Now You need to localize NAS IP, run the same `nmap`:

```bash
nmap -sP 10.0.0.0/24
# or
arp -a
```

And get diff (lets say `10.0.0.101`)

If You can ssh to NAS - go to Ansible part.

If not - debug time.

## Ansible part

Just run:

```bash
ansible-playbook all_in_one.yml --ask-become-pass -e "target=10.0.0.101" -i 10.0.0.101,
```

And watch the magic.

After its done, it is done :)

## Helpful stuff

### Aliases

```bash
# Alias for loading password and mounting
function zload() {
  sudo zfs load-key -L prompt $1 && sudo zfs mount $1
}

# Alias for unloading password and unmounting
function zunload() {
  sudo zfs unmount -f $1 && sudo zfs unload-key $1
}

# Wipes whole zfs datasets and pools
zfs destroy -r nas
```

### Manually converting qcow2 to img

```bash
qemu-img convert nas-ubuntu-server.qcow2 -O raw nas-ubuntu-server.img
```

### Existing ZFS pool

It may happen that You already have old ZFS pool:

```bash
TASK [zfs : Create ZFS pool] ***************************************************
fatal: [0.0.0.0]: FAILED! => changed=true
  cmd: zpool create -o autoexpand=on -o autoreplace=on -o delegation=on -o dedupditto=1.5 -o failmode=continue -o listsnaps=on nas raidz2 /dev/sda /dev/sdb /dev/sdc /dev/sdd
  msg: non-zero return code
  rc: 1
  stderr: |-
    invalid vdev specification
    use '-f' to override the following errors:
    /dev/sda1 is part of potentially active pool 'nas'
    /dev/sdb1 is part of potentially active pool 'nas'
    /dev/sdc1 is part of potentially active pool 'nas'
    /dev/sdd1 is part of potentially active pool 'nas'
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
```

In that situation just type:

```bash
$ sudo zpool import
   pool: nas
     id: 0000000000000000000
  state: ONLINE
status: The pool was last accessed by another system.
 action: The pool can be imported using its name or numeric identifier and
        the '-f' flag.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-EY
 config:

        nas         ONLINE
          raidz2-0  ONLINE
            sda     ONLINE
            sdb     ONLINE
            sdc     ONLINE
            sdd     ONLINE
$ sudo zpool import -f 0000000000000000000
$ zload nas/data
```

### Debug

While You cannot connect to NAS, unplug USB from it, and plug back to PC. Go to tmp folder (BIOS is there), and run command (replace `disk5` with whatever suits your case):

```bash
sudo kvm -bios ./bios.bin -L . -drive format=raw,file=/dev/disk5 -m 4G
```

Log into system, and dive into logs.

And that's it.
