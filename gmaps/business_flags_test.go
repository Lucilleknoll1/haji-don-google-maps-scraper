package gmaps_test

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/gosom/google-maps-scraper/gmaps"
)

func buildEntryRaw(t *testing.T, mutate func(darray []any)) []byte {
	t.Helper()

	darray := make([]any, 227)
	darray[11] = "Test Business"
	darray[13] = []any{"Test Category"}

	if mutate != nil {
		mutate(darray)
	}

	jd := []any{nil, nil, nil, nil, nil, nil, darray}

	raw, err := json.Marshal(jd)
	require.NoError(t, err)

	return raw
}

func TestBusinessFlagsUnclaimedFixture(t *testing.T) {
	raw, err := os.ReadFile("../testdata/panic2.json")
	require.NoError(t, err)

	entry, err := gmaps.EntryFromJSON(raw)
	require.NoError(t, err)

	require.Equal(t, "unclaimed", entry.ClaimState)
	require.Equal(t, "claim_link", entry.ClaimEvidence)
	require.NotEmpty(t, entry.ClaimURL)
	require.Equal(t, "Dogs allowed", entry.Highlight)
	require.Empty(t, entry.StatusBadge)
	require.Equal(t, "unknown", entry.BusinessStatus)
	require.NotEqual(t, "Dogs allowed", entry.Status)
}

func TestBusinessFlagsClaimedFixture(t *testing.T) {
	raw, err := os.ReadFile("../testdata/raw.json")
	require.NoError(t, err)

	entry, err := gmaps.EntryFromJSON(raw)
	require.NoError(t, err)

	require.Equal(t, "claimed", entry.ClaimState)
	require.Equal(t, "claimed_flag", entry.ClaimEvidence)
	require.Equal(t, "unknown", entry.BusinessStatus)
	require.NotEmpty(t, entry.HoursSummary)
	require.Equal(t, entry.HoursSummary, entry.Status)
}

func TestBusinessStatusClassification(t *testing.T) {
	tests := []struct {
		name       string
		badge      string
		wantStatus string
		wantState  string
	}{
		{name: "permanent enum", badge: "CLOSED", wantStatus: "permanently_closed", wantState: "CLOSED"},
		{name: "permanent label", badge: "Permanently closed", wantStatus: "permanently_closed", wantState: "Permanently closed"},
		{name: "temporary label", badge: "Temporarily closed", wantStatus: "temporarily_closed", wantState: "Temporarily closed"},
		{name: "temporary localized", badge: "ĐANG ĐÓNG CỬA", wantStatus: "temporarily_closed", wantState: "ĐANG ĐÓNG CỬA"},
		{name: "ordinary highlight", badge: "Brunch", wantStatus: "unknown", wantState: ""},
		{name: "no badge", badge: "", wantStatus: "unknown", wantState: ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			raw := buildEntryRaw(t, func(darray []any) {
				darray[88] = []any{tt.badge}
			})

			entry, err := gmaps.EntryFromJSON(raw)
			require.NoError(t, err)

			require.Equal(t, tt.wantStatus, entry.BusinessStatus)
			require.Equal(t, tt.wantState, entry.StatusBadge)
			require.Equal(t, tt.badge, entry.Highlight)

			if tt.wantState == "" {
				require.Empty(t, entry.Status)
			} else {
				require.Equal(t, tt.wantState, entry.Status)
			}
		})
	}
}

func TestClaimStateFromFlags(t *testing.T) {
	tests := []struct {
		name      string
		mutate    func(darray []any)
		wantState string
		want      string
	}{
		{
			name: "claim link",
			mutate: func(darray []any) {
				darray[49] = []any{"https://business.google.com/create?fp=1"}
			},
			wantState: "unclaimed",
			want:      "claim_link",
		},
		{
			name: "claimed flag one",
			mutate: func(darray []any) {
				darray[165] = []any{float64(1)}
			},
			wantState: "claimed",
			want:      "claimed_flag",
		},
		{
			name: "claimed flag zero alone is unknown",
			mutate: func(darray []any) {
				darray[165] = []any{float64(0)}
			},
			wantState: "unknown",
			want:      "",
		},
		{
			name: "claimed flag zero with owner logo",
			mutate: func(darray []any) {
				darray[165] = []any{float64(0)}
				darray[157] = "https://lh3.googleusercontent.com/logo"
			},
			wantState: "claimed",
			want:      "owner_assets",
		},
		{
			name: "claim link with claimed flag",
			mutate: func(darray []any) {
				darray[49] = []any{"https://business.google.com/create?fp=1"}
				darray[165] = []any{float64(1)}
			},
			wantState: "conflict",
			want:      "claim_link_and_claimed_signal",
		},
		{
			name: "owner logo without flag",
			mutate: func(darray []any) {
				darray[157] = "https://lh3.googleusercontent.com/logo"
			},
			wantState: "claimed",
			want:      "owner_assets",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			raw := buildEntryRaw(t, tt.mutate)

			entry, err := gmaps.EntryFromJSON(raw)
			require.NoError(t, err)

			require.Equal(t, tt.wantState, entry.ClaimState)
			require.Equal(t, tt.want, entry.ClaimEvidence)
		})
	}
}
