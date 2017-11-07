
declare -A dockerfiles
dockerfiles=(["heywill/will-base:2.7-alpine"]="./will-base/base-2.7/"
    ["heywill/will-base:3.7-alpine"]="./will-base/base-3.x/"
    ["heywill/will:python2.7"]="./will/will-py2/"
    ["heywill/will:python3.7"]="./will/will-py3/")
build_containers() {

    for tag in "${!dockerfiles[@]}"; 
        do 
            echo "building $tag with context ${dockerfiles[$tag]}";
            docker build -t $tag ${dockerfiles[$tag]};
            echo ""
        done;
}

tag_latest(){

    docker tag heywill/will-base:3.7-alpine heywill/will-base:latest
    echo "tagged heywill/will-base:3.7-alpine as heywill/will-base:latest"
    docker tag heywill/will:python3.7 heywill/will:latest
    
    echo "tagged heywill/will:3.7 as heywill/will:latest"
}


push_containers(){
    tag_latest
    for tag in "${!dockerfiles[@]}"; 
        do 
            echo "pushing $tag";
            docker push $tag;
            echo ""
        done;
    
   docker push heywill/will-base:latest
   docker push heywill/will:latest
}

case $1 in 
    "--all")
        build_containers
        push_containers
        ;;
    
    "--build")
        build_containers
        ;;
    
    "--push")
        push_containers
        ;;

    *)
        echo "You did something wrong"
        exit 1
        ;;
esac

