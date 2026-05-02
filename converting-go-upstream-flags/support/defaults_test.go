package setup

import "testing"

func TestDefaultUpstreamAddr(t *testing.T) {
	tests := []struct {
		name string
		env  map[string]string
		args []int
		want string
	}{
		{
			name: "defaults to sandbox tailnet host on standard port",
			want: "agent-iam-sandbox:8080",
		},
		{
			name: "uses account name for tailnet host",
			env: map[string]string{
				"ACCOUNT_NAME": "office",
			},
			want: "agent-iam-office:8080",
		},
		{
			name: "uses explicit port for tailnet host",
			env: map[string]string{
				"ACCOUNT_NAME": "office",
			},
			args: []int{10570},
			want: "agent-iam-office:10570",
		},
		{
			name: "uses kubernetes service discovery in cluster",
			env: map[string]string{
				"KUBERNETES_SERVICE_HOST": "10.0.0.1",
			},
			want: "agent.iam:8080",
		},
		{
			name: "uses explicit port for kubernetes service discovery",
			env: map[string]string{
				"KUBERNETES_SERVICE_HOST": "10.0.0.1",
			},
			args: []int{10570},
			want: "agent.iam:10570",
		},
		{
			name: "kubernetes service discovery takes precedence over account name",
			env: map[string]string{
				"ACCOUNT_NAME":            "office",
				"KUBERNETES_SERVICE_HOST": "10.0.0.1",
			},
			want: "agent.iam:8080",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Setenv("ACCOUNT_NAME", "")
			t.Setenv("KUBERNETES_SERVICE_HOST", "")
			for key, value := range tt.env {
				t.Setenv(key, value)
			}

			got := DefaultUpstreamAddr("agent", "iam", tt.args...)
			if got != tt.want {
				t.Fatalf("DefaultUpstreamAddr() = %q, want %q", got, tt.want)
			}
		})
	}
}
