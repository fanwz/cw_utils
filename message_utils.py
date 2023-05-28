import os


class RemoteHub(object):
    def __init__(self) -> None:
        super().__init__()

    def push(self, data):
        raise NotImplementedError


class RemoteServer(RemoteHub):
    '''
    "remote_hub" : {
      "Type" : "SSH",
      "IP" : "192.168.32.52",
      "Port" : "22",
      "User" : "test",
      "Password" : "test",
      "recv_dir" : "/recv_dir"
   }
    '''

    def __init__(self, remote_config) -> None:
        super().__init__()
        self.srv_type = remote_config["Type"]
        if self.srv_type.upper() == "SSH":
            self.ip = remote_config["IP"]
            self.port = remote_config["Port"]
            self.user = remote_config["User"]
            self.password = remote_config["Password"]
            self.recv_dir = remote_config["recv_dir"]
        else:
            print("remote server type {} is not support!".format(self.srv_type))

    def push(self, data):
        if self.srv_type.upper() == "SSH":
            cmd = 'rsync -avzP -e \'ssh -p {0}\' {1} {2}@{3}:{4}'.format(self.port,
                                                                         data, self.user, self.ip, self.recv_dir)
            ret = os.system(cmd)
            if ret == 0:
                print("push file sucess")
            else:
                print("push file error.ret={}".format(ret))
        else:
            print("remote server type {} is not support!".format(self.srv_type))
