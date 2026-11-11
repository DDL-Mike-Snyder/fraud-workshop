GOOD=e42159b

git switch main
git fetch origin
git branch backup-pre-rollback   # safety

git restore --source=$GOOD --staged --worktree .   # fallback: git checkout $GOOD -- .
git status                                           # make sure only what you want is staged
git commit -m "Rollback main to $GOOD"
git push origin main
