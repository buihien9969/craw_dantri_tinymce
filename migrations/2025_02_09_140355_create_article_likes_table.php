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
        Schema::create('article_likes', function (Blueprint $table) {
            $table->id('like_id');
            $table->foreignId('article_id')
                ->constrained('articles', 'article_id')
                ->onDelete('CASCADE'); // Thêm ON DELETE CASCADE

            $table->foreignId('user_id')
                ->constrained('users', 'user_id')
                ->onDelete('CASCADE'); // Thêm ON DELETE CASCADE

            $table->timestamp('liked_at')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('article_likes');
    }
};
