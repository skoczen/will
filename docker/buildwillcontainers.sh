#!/bin/bash -e

declare -a dockerfiles
dockerfiles=(
    ["heywill/will:python2.7$CTAG"]="/will/will-py2/"
    ["heywill/will:python3.7$CTAG"]="/will/will-py3/")

build_containers() {

    for tag in "${!dockerfiles[@]}"; 
        do 
            echo "building $tag with context ${dockerfiles[$tag]}";
            docker build -t $tag $(dirname $(readlink -f ${BASH_SOURCE[0]}))${dockerfiles[$tag]};
            echo ""
        done;
}

tag_production(){
    docker tag heywill/will:python2.7$CTAG heywill/will:python2.7
    echo "tagged heywill/will:python2.7$CTAG as heywill/will:latest"
    
    docker tag heywill/will:python3.7$CTAG heywill/will:python3.7
    docker tag heywill/will:python3.7$CTAG heywill/will:latest
    echo "tagged heywill/will:python3.7$CTAG as heywill/will:latest & heywill/will:python3.7"
}


push_containers(){
   tag_production
   
   docker push heywill/will-base:latest
   docker push heywill/will:latest
}
echo "Building with COMMIT TAG: $CTAG"
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

