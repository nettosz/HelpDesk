import click
import requests
import threading
import logging
import warnings

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

@click.command()
@click.option('--url', '-u', help='URL to stress test')
@click.option('--num-threads', '-n', default=10, help='Number of concurrent threads')
@click.option('--num-requests', '-r', default=100, help='Number of requests per thread')
def stress_test(url, num_threads, num_requests):
    if not url:
        click.echo("Please provide a URL to stress test.")
        return

    logging.info(f"Starting stress test on {url} with {num_threads} threads and {num_requests} requests per thread...")
    
    def send_requests():
        for i in range(num_requests):
            try:
                response = requests.get(url, verify=False)
                if response.status_code == 200:
                    pass
            except requests.RequestException as e:
                logging.error(f">> {threading.current_thread().name} - Request {i+1}: Request failed: {e}")
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=send_requests, name=f'Thread-{i+1}')
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logging.info("Stress test completed.")

if __name__ == '__main__':
    stress_test()
