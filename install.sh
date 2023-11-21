#!/bin/bash
clear

CONTAINER_NAME="sycgram-pro"
GITHUB_IMAGE_NAME="liuzy/${CONTAINER_NAME}"
GITHUB_IMAGE_PATH="${GITHUB_IMAGE_NAME}"
# 修改为当前路径
PROJECT_PATH="$PWD"
PROJECT_VERSION="v3.1.4"

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

pre_check() {
    [[ $EUID -ne 0 ]] && echo -e "${red}错误: ${plain} 需要root权限\n" && exit 1

    command -v git >/dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo -e "正在安装Git..."
        apt install git -y >/dev/null 2>&1
        echo -e "${green}Git${plain} 安装成功"
    fi

    command -v curl >/dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo -e "正在安装curl..."
        apt install curl -y >/dev/null 2>&1
        echo -e "${green}curl${plain} 安装成功"
    fi

    command -v docker >/dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo -e "正在安装Docker..."
        bash <(curl -fsL https://get.docker.com) >/dev/null 2>&1
        echo -e "${green}Docker${plain} 安装成功"
    fi

    command -v tar >/dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo -e "正在安装tar..."
        apt install tar -y >/dev/null 2>&1
        echo -e "${green}tar${plain} 安装成功"
    fi
}

delete_old_image_and_container(){
    # 获取最新指令说明
    # 远程file
    remote_file="https://raw.githubusercontent.com/fireinrain/sycgram-pro/main/data/command.yml"
    # 本地file
    local_cmd_file="${PROJECT_PATH}/data/command.yml"
    if [[ -f ${local_cmd_file} ]]; then
        t=$(date "+%H_%M_%M")
        mkdir -p "${PROJECT_PATH}/data/command" >/dev/null 2>&1

        echo -e "${yello}正在备份${plain} >>> ${local_cmd_file}"
        cp ${local_cmd_file} "${PROJECT_PATH}/data/command/command.yml.${t}"
    fi
    curl -fsL ${remote_file} > ${local_cmd_file}

    echo -e "${yellow}正在删除旧版本容器...${plain}"
    docker rm -f $(docker ps -a | grep ${CONTAINER_NAME} | awk '{print $1}')

    echo -e "${yellow}正在删除旧版本镜像...${plain}"
    docker image rm -f $(docker images | grep ${CONTAINER_NAME} | awk '{print $3}')
}

check_and_create_config(){
if [ ! -f ${PROJECT_PATH}/data/config.ini ]; then

mkdir -p "${PROJECT_PATH}/data" >/dev/null 2>&1

read -p "请输入你的 api_id：" api_id
read -p "请输入你的 api_hash：" api_hash

cat > ${PROJECT_PATH}/data/config.ini <<EOF
[pyrogram]
api_id=${api_id}
api_hash=${api_hash}
[plugins]
root=plugins
EOF
fi
}

stop_sycgram_pro(){
    res=$(docker stop $(docker ps -a | grep ${GITHUB_IMAGE_NAME} | awk '{print $1}'))
    if [[ $res ]];then
        echo -e "${yellow}已停止sycgram-pro...${plain}"
    else
        echo -e "${red}无法停止sycgram-pro...${plain}"
    fi
}

restart_sycgram_pro(){
    res=$(docker restart $(docker ps -a | grep ${GITHUB_IMAGE_NAME} | awk '{print $1}'))
    if [[ $res ]];then
        echo -e "${yellow}已重启sycgram-pro...${plain}"
    else
        echo -e "${red}无法重启sycgram-pro...${plain}"
    fi
}

view_docker_log(){
    docker logs -f $(docker ps -a | grep ${GITHUB_IMAGE_NAME} | awk '{print $1}')
}

uninstall_sycgram_pro(){
    delete_old_image_and_container;
    rm -rf ${project_path}
}

reinstall_sycgram_pro(){
    rm -rf ${PROJECT_PATH}
    install_sycgram_pro "-it"
}

install_sycgram_pro(){

    # 设置默认容器名称
    default_container_name="sycgram-pro"

    # 提示用户输入容器名称
    printf "请输入 sycgram-pro 容器的名称 [默认为$default_container_name]: "

    # 使用 read 命令读取用户输入，如果用户未输入则使用默认值
    read -r container_name

    # 如果用户未输入任何内容，则使用默认值
    if [ -z "$container_name" ]; then
        container_name="$default_container_name"
    fi

    #printf "请输入 sycgram-pro 容器的名称："
    #read -r container_name <&1

    pre_check;
    check_and_create_config;
    delete_old_image_and_container;

    echo -e "${yellow}正在拉取镜像...${plain}"
    docker pull ${GITHUB_IMAGE_PATH}:latest

    echo -e "${yellow}正在启动容器...${plain}"
    docker run $1 \
    --name ${container_name} \
    --env TZ="Asia/Shanghai" \
    --restart always \
    --hostname ${container_name} \
    -v ${PROJECT_PATH}/data:/sycgram-pro/data \
    ${GITHUB_IMAGE_PATH}:latest
}

show_menu() {
    echo -e "${green}Sycgram-pro${plain} | ${green}管理脚本${plain} | ${red}${PROJECT_VERSION}${plain}"
    echo -e "  ${green}1.${plain}  安装"
    echo -e "  ${green}2.${plain}  更新"
    echo -e "  ${green}3.${plain}  停止"
    echo -e "  ${green}4.${plain}  重启"
    echo -e "  ${green}5.${plain}  查看日志"
    echo -e "  ${green}6.${plain}  重新安装"
    echo -e "  ${green}7.${plain}  卸载"
    echo -e "  ${green}0.${plain}  退出脚本"
    read -ep "请输入选择 [0-7]: " option
    case "${option}" in
    0)
        exit 0
        ;;
    1)
        install_sycgram_pro "-it"
        ;;
    2)
        install_sycgram_pro "-itd"
        ;;
    3)
        stop_sycgram_pro
        ;;
    4)
        restart_sycgram_pro
        ;;
    5)
        view_docker_log
        ;;
    6)
        reinstall_sycgram_pro
        ;;
    7)
        uninstall_sycgram_pro
        ;;
    *)
        echo -e "${yellow}已退出脚本...${plain}"
        exit
        ;;
    esac
}

show_menu;
