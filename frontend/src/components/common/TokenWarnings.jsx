import { TransitionGroup, CSSTransition } from 'react-transition-group';

export default function TokenWarnings({ warnings, onRemove }) {
  return (
    <>
      <TransitionGroup className="fixed bottom-4 right-4 flex flex-col space-y-2 z-50">
        {warnings.map((msg) => (
          <CSSTransition key={msg} timeout={300} classNames="toast">
            <div
              className="bg-yellow-300 text-yellow-900 p-4 rounded shadow-lg cursor-pointer"
              onClick={() => onRemove(msg)}
              role="alert"
            >
              {msg}
            </div>
          </CSSTransition>
        ))}
      </TransitionGroup>

      <style>{`
        .toast-enter {
          opacity: 0;
          transform: translateY(100%);
        }
        .toast-enter-active {
          opacity: 1;
          transform: translateY(0);
          transition: opacity 300ms, transform 300ms;
        }
        .toast-exit {
          opacity: 1;
          transform: translateY(0);
        }
        .toast-exit-active {
          opacity: 0;
          transform: translateY(-100%);
          transition: opacity 300ms, transform 300ms;
        }
      `}</style>
    </>
  );
}
