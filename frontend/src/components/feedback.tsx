export function Spinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="feedback" role="status">
      <span className="spinner" aria-hidden="true" />
      {label}
    </div>
  );
}

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="feedback error" role="alert">
      {message}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return <div className="feedback empty">{message}</div>;
}
