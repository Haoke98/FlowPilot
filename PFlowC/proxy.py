import click

from PFlowC.proxy_helper.macosx import set_web_proxy, set_cmd_proxy


@click.command
@click.option("--host", "-h", default="127.0.0.1", help="The host address of the proxy")
@click.option("--port", "-p", default=8080, help="The port of the proxy")
@click.option("--socks_port", "-s", default=8090, help="The port of the socks server")
@click.option("--bypass-domains", type=list, default=['127.0.0.1', "192.168.0.0/16"],
              help="The domains to bypass the proxy.")
def main(host, port, socks_port, bypass_domains):
    set_web_proxy(host, port, bypass_domains)
    set_cmd_proxy(host, port, bypass_domains)
    print("Proxy settings updated successfully.")


if __name__ == "__main__":
    main()
