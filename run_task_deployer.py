from task_deployer import TaskDeployer

if __name__ == '__main__':

    epoch_time = 21600
    epoch_percentage = 0.24

    deployer = TaskDeployer(epoch_time, epoch_percentage)
    deployer.run()