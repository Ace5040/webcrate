if [%1]==[] goto :general
  docker exec -it sitesbox sudo --user dev bash -c "export HOME=/sites/%1; cd ~;fish"
:general
  docker exec -it sitesbox fish
