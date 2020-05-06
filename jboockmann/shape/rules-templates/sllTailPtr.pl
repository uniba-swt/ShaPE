entry(This)  :-  node(This), next(This, Next), tail(This, Tail), p(Tail, Next), true.
p(This, P1)  :-  node(This), next(This, P1), tail(This, P1), true.
p(This, P1)  :-  node(This), next(This, Next), tail(This, P1), p(Next, P1), true.
p(This, P1)  :-  node(This), next(This, null), tail(This, This), true, p(P1, This), true.