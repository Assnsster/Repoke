echo "===================================="
echo "Download windows files"
echo "===================================="
sudo apt update -y
sudo apt upgrade -y
wget -O w10x64.img https://bit.ly/akuhnetW10x64
echo "===================================="
echo "Download ngrok"
echo "===================================="
wget -O ngrok.tgz https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz > /dev/null 2>&1
tar -zxvf ngrok.tgz > /dev/null 2>&1
read -p "Paste authtoken here (Copy and Ctrl+V to paste then press Enter): " CRP
./ngrok config add-authtoken $CRP 
nohup ./ngrok tcp 3388 &>/dev/null &
./ngrok tcp 3388 &>/dev/null &
echo "===================================="
echo Downloading File From akuh.net
echo "===================================="
apt-get install qemu > /dev/null 2>&1
echo "===================================="
echo "Wait"
echo "Starting Windows"
echo "===================================="
echo "===================================="
echo RDP Address:
curl --silent --show-error http://127.0.0.1:4040/api/tunnels | sed -nE 's/.*public_url":"tcp:..([^"]*).*/\1/p'
echo "===================================="
echo "===================================="
echo "Ctrl+C To Copy"
echo "Wait 1-2 minute to finish bot"
echo "Dont Close This Tab"
echo "===================================="
echo "===================================="
echo "Username: akuh"
echo "Password: Akuh.Net"
echo "===================================="
qemu-system-x86_64 -hda w10x64.img -m 8G -smp cores=4 -net user,hostfwd=tcp::3388-:3389 -net nic -object rng-random,id=rng0,filename=/dev/urandom -device virtio-rng-pci,rng=rng0 -vga vmware -nographic  > /dev/null 2>&1
sleep 43200
