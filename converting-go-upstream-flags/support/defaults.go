package setup

import (
	"fmt"
	"os"
)

// DefaultUpstreamAddr provides a useful default for a flag that configures a service dependency.
// It returns a string of the form `service-namespace-account:port` for services exposed via our
// development tailnet, or `service.namespace:port` when running inside a Kubernetes cluster.
//
// Using this function to provide default flag values has two benefits:
//  1. Useful documentation of the purpose of each flag
//  2. Allows developers to `go run` your service provided all upstreams are reachable via Tailnet
//
// To use it, make sure your `resolv.conf` search path includes the tailnet where the downstreams
// are exposed. The Tailscale agent should configure this automatically when you connect.
// Also ensure that the `ACCOUNT_NAME` environment variable is correct (or that you prefer its
// default value, which is `sandbox`).
//
// @see https://github.com/crossnokaye/localdev
func DefaultUpstreamAddr(service, namespace string, ports ...int) string {
	port := 8080
	if len(ports) > 0 {
		port = ports[0]
	}

	if os.Getenv("KUBERNETES_SERVICE_HOST") != "" {
		return fmt.Sprintf("%s.%s:%d", service, namespace, port)
	}

	account := os.Getenv("ACCOUNT_NAME")
	if account == "" {
		account = "sandbox"
	}
	return fmt.Sprintf("%s-%s-%s:%d", service, namespace, account, port)
}
