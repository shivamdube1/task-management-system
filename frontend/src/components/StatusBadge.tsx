/** Status and priority badge components. */

interface BadgeProps {
  type: 'status' | 'priority';
  value: string;
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  in_progress: 'In Progress',
  completed: 'Completed',
};

const PRIORITY_LABELS: Record<string, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
};

export default function StatusBadge({ type, value }: BadgeProps) {
  const label =
    type === 'status'
      ? STATUS_LABELS[value] || value
      : PRIORITY_LABELS[value] || value;

  return <span className={`badge badge-${value}`}>{label}</span>;
}
