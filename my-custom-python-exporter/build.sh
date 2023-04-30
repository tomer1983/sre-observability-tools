#!bash
set -e
PROJECT_NAME='sre-hcp-exporter'
PROJECT_TAG='v0.1'
RANDOM=$(echo $RANDOM)
REPO_URL='tomer1983/sre-tools/'

# mkdir -p code/dependencies
# pip3 download -r code/requirements.txt -d "code/dependencies" 
# tar cvfz code/dependencies.tar.gz code/dependencies



echo -e "PROJECT: $PROJECT_NAME:$PROJECT_TAG hash:$RANDOM"

# #login to artifactory
#docker login -u <user> REPO_URL -p <pass>

# #build the image
docker build --force-rm -t $PROJECT_NAME:$PROJECT_TAG code/.


# # This command tags the Docker image with the given project name and tag, and specifies the destination registry and repository where the image should be stored.
docker tag $PROJECT_NAME:$PROJECT_TAG REPO_URL/sre-tools/$PROJECT_NAME:$PROJECT_TAG

# # This command pushes the Docker image to the specified destination registry and repository.
docker push REPO_URL/sre-tools/$PROJECT_NAME:$PROJECT_TAG

# # This command displays a message to indicate that the image has been successfully pushed to the destination repository and registry.
echo -e "DONE - image pushed to REPO_URL/sre-tools/$PROJECT_NAME:$PROJECT_TAG"

# # building a kuberntes.yaml file with the right arguments
sed "s/__PROJECT_NAME__/$PROJECT_NAME/g" manifest/kubernetes.templete.yaml > manifest/kubernetes.yaml
sed -i "s/__PROJECT_TAG__/$PROJECT_TAG/g" manifest/kubernetes.yaml
sed -i "s/__PROJECT_TAG__/$PROJECT_TAG/g" manifest/cm.yaml


# Redeploy
oc delete -f ./manifest/kubernetes.yaml --force --grace-period=0 2>/dev/null || true
oc delete -f ./manifest/cm.yaml --force --grace-period=0 2>/dev/null || true
sleep 5
oc apply -f ./manifest/cm.yaml 
oc apply -f ./manifest/kubernetes.yaml 
sleep 5
while [ -z "$(oc get pods --sort-by=.metadata.creationTimestamp -o name | grep $PROJECT_NAME |  tail -1 | cut -d/ -f2)" ]; do echo waiting for pod to start & sleep 1 ; done 
POD=$( oc get pods --sort-by=.metadata.creationTimestamp -o name | grep $PROJECT_NAME |  tail -1 | cut -d/ -f2)
echo "#POD : $POD"
ROUTE=$(oc get route | grep sre)
echo "ROUTE IS : $ROUTE"
oc wait --for=condition=Ready pod $POD && oc logs -f $POD
