Xvfb :1 -screen 0 1024x768x16 &
cd /opt/Allegorithmic/Substance_Automation_Toolkit/samples/legacy/samples
echo "Before"
ls
sbsbaker ambient-occlusion Big_Rock.fbx
echo "After"
ls