# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  # Ubuntu LTS 14.04
  config.vm.box = "bento/ubuntu-18.04"


  config.vm.synced_folder ".", "/home/vagrant/python-opencage-geocoder"

  # provision using a simple shell script
  config.vm.provision :shell, :path => "vagrant-provision.sh"


  # configure shared package cache if possible
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.enable :apt
    config.cache.scope = :box
  end


  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    # vb.customize ["modifyvm", :id, "--memory", "1024"]
  end


end
