<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('comment_reactions', function (Blueprint $table) {
            $table->id('reaction_id');
            $table->foreignId('comment_id')->constrained('comments', 'comment_id');
            $table->foreignId('user_id')->constrained('users', 'user_id');
            $table->boolean('is_like')->default(true);
            $table->timestamp('reacted_at')->useCurrent();
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('comment_reactions');
    }
};
