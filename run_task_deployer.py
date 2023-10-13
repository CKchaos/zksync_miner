from task_deployer import TaskDeployer
import utils

if __name__ == '__main__':
    params = utils.load_json('./params/run_task_deployer.json')

    epoch_time = params['epoch_time']
    epoch_percentage = params['epoch_percentage']
    swap_prob = params['swap_prob']
    usdc_prob = params['usdc_prob']

    deployer = TaskDeployer(epoch_time, epoch_percentage, swap_prob, usdc_prob)
    deployer.run()