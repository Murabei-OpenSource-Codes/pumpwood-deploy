"""Resorces template for volumes."""

volume_gcp = """
kind: PersistentVolume
apiVersion: v1
metadata:
  name: {disk_name}
  labels:
    usage: {disk_name}
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: {disk_size}
  storageClassName: standard
  gcePersistentDisk:
    fsType: ext4
    pdName: {disk_name}
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: {volume_claim_name}
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: {disk_size}
  volumeName: {disk_name}
"""

volume_azure = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: {disk_name}
  labels:
    usage: {disk_name}
spec:
  capacity:
    storage: {disk_size}
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: managed-csi
  csi:
    driver: disk.csi.azure.com
    readOnly: false
    volumeHandle: /subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/disks/{disk_name}
    volumeAttributes:
      fsType: ext4
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
    name: {volume_claim_name}
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: managed-csi
  resources:
    requests:
      storage: {disk_size}
  volumeName: {disk_name}
"""

volume_aws = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: {aws_volume_id}
  labels:
    usage: {aws_volume_id}
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: {disk_size}
  csi:
    driver: ebs.csi.aws.com
    fsType: ext4
    volumeHandle: {aws_volume_id}
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
    name: {volume_claim_name}
spec:
  storageClassName: ""
  volumeName: {aws_volume_id}
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
"""
