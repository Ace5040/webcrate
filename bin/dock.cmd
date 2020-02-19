if [%1]==[] goto :general
  docker exec -it sitesbox sudo --user dev bash -c "export HOME=/sites/%1; cd ~;bash -l"
:general
  docker exec -it sitesbox bash -l
