apiVersion: v1
kind: PersistentVolume
metadata:
  name: flask-pv
  labels:
    type: nfs
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  nfs:
    path:  /srv/nfs/dayam7         #local reference
    server: 10.48.10.140
  persistentVolumeReclaimPolicy: Retain
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: flask-pvc    
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
  selector:
    matchLabels:
      type: nfs
---      
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-prod-deployment
  labels:
    app: flask
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
        - name: flask
          image: cithit/dayam7:latest
          ports:
            - containerPort: 5000
          volumeMounts:
            - name: nfs-storage
              mountPath: /nfs       
      volumes:
        - name: nfs-storage
          persistentVolumeClaim:
            claimName: flask-pvc    
---
apiVersion: v1
kind: Service
metadata:
  name: flask-prod-service
spec:
  type: LoadBalancer 
  loadBalancerIP: 10.48.10.209                                     
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  selector:
    app: flask
